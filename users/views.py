from django.http import HttpResponseServerError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Agent, Tenant, Apartment, Room, Booking
from .forms import AgentSignUpForm, TenantSignUpForm, LoginForm, PropertyForm, RoomForm, AvailableTimeForm, BookingForm, OccupationForm, BillForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .decorators import tenant_required, agent_required
from django.http import Http404
from django.shortcuts import render
from .models import Apartment, Booking, AvailableTime, Room, Occupation, Contract
from payments.models import Bill
# import messages
from django.contrib import messages
# timezone
from django.utils import timezone
# timedelta
from datetime import timedelta
from django.views.generic import TemplateView

from django.http import FileResponse
from django.template.loader import get_template
from django.urls import reverse
from django.http import HttpResponse
from xhtml2pdf import pisa


# Create your views here.
def landing_page(request):
    apartments = Apartment.objects.all()
    context = {
        'apartments': apartments
    }
    return render(request, 'users/home.html', context)


def generate_contract_pdf(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)

    template = get_template('users/contract_template.html')
    context = {
        'contract': contract,
        'agent_first_name': contract.agent_first_name,
        'agent_last_name': contract.agent_last_name,
        'tenant_first_name': contract.tenant_first_name,
        'tenant_last_name': contract.tenant_last_name,
    }
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{contract_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error')

    return response


def agent_signup_view(request):
    if request.method == 'POST':
        form = AgentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'users/agent_home.html')
    else:

        form = AgentSignUpForm()
    return render(request, 'users/agent_signup.html', {'form': form})


def tenant_signup_view(request):
    if request.method == 'POST':
        form = TenantSignUpForm(request.POST)
        print(form)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'users/tenant_home.html')
    else:

        form = TenantSignUpForm()
    return render(request, 'users/tenant_signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Log the user in
            login(request, form.get_user())
            if request.user.is_agent:
                messages.success(request, f'Welcome {request.user.username}')
                return redirect('agent_home')
            elif request.user.is_tenant:
                messages.success(request, f'Welcome {request.user.username}')
                return redirect('tenant_home')

    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
@tenant_required
def tenant_home(request):
    properties = Apartment.objects.all()
    bookings = Booking.objects.filter(tenant=request.user.tenant)
    occupations = Occupation.objects.filter(tenant=request.user.tenant)
    occupation = Occupation.objects.filter(tenant=request.user.tenant).first()
    bills = Bill.objects.filter(tenant=request.user.tenant)
    contract = Contract.objects.filter(tenant=request.user.tenant).first()

    print(bookings)

    context = {
        'properties': properties,
        'bookings': bookings,
        'bills': bills,
        'occupation': occupation,

        'contract': contract,
    }
    return render(request, 'users/tenant_home.html', context)


@login_required
@agent_required
def agent_home(request):
    apartments = Apartment.objects.filter(agent=request.user.agent)
    occupants = Occupation.objects.filter(
        room__apartment__agent=request.user.agent)
    bills = Bill.objects.filter(room__apartment__agent=request.user.agent)
    print(bills)
    # sum of all bill amounts
    total = 0
    for bill in bills:
        total += bill.amount
    print(total)

    print(occupants)
    # all bookings for the agent
    bookings = Booking.objects.filter(
        available_time__room__apartment__agent=request.user.agent)
    print(bookings)
    print(apartments)
    context = {
        'apartments': apartments,
        'bookings': bookings,
        'occupants': occupants,
        'bills': bills,
        'total': total,

    }
    return render(request, 'users/agent_home.html', context)


def property_details(request, id):
    apartment = Apartment.objects.get(id=id)
    rooms = Room.objects.filter(apartment=apartment)
    print(f"Agent Rooms: {rooms}")
    if request.user.is_tenant:
        rooms = rooms.filter(is_occupied=False)

    context = {
        'apartment': apartment,
        'rooms': rooms,
        'property_id': id,
    }
    return render(request, 'users/property_details.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, f'You have been logged out')
    return redirect('landing_page')


# @login_required
# @agent_required
# def create_property()


@login_required
@agent_required
def create_property(request):
    user = request.user

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)

        if form.is_valid():
            property_instance = form.save(commit=False)

            try:
                agent = get_object_or_404(Agent, user=user)
                property_instance.agent = agent
                property_instance.save()
                messages.success(request, f'Property created successfully')
                return redirect('agent_home')
            except IntegrityError:
                messages.error(request, f'Error creating property')
                return HttpResponseServerError("Agent not found for the user.")
    else:
        form = PropertyForm()

    return render(request, 'users/create_property.html', {'form': form})


def search_results(request):
    search_query = request.GET.get('search_query')
    property_type = request.GET.get('property_type')

    # Filter properties based on search_query and property_type
    properties = Apartment.objects.filter(
        name__icontains=search_query,
        property_type=property_type
    )

    context = {
        'properties': properties,
    }
    return render(request, 'users/search_results.html', context)


@login_required
def room_details(request, id):
    room = Room.objects.get(id=id)
    available_times = AvailableTime.objects.filter(room=room)
    booking = None

    occupation = Occupation.objects.filter(room=room)
    bills = Bill.objects.filter(
        room=room, tenant=occupation.first().tenant) if occupation else []
    is_authenticated_tenant = request.user.is_authenticated and hasattr(
        request.user, 'tenant')

    if is_authenticated_tenant:
        booking = Booking.objects.filter(
            tenant=request.user.tenant, available_time__room=room).first()

    has_booking = Booking.objects.filter(
        tenant=request.user.tenant, available_time__room=room).exists() if is_authenticated_tenant else False

    # Initialize the BookingForm and pass the room_id to the form
    form = BookingForm(request.POST or None, room_id=id)

    bill_form = BillForm(request.POST or None)

    # Add the OccupationForm to the view
    occupation_form = OccupationForm()

    if request.method == 'POST' and request.user.is_agent:
        occupation_form = OccupationForm(request.POST)
        if occupation_form.is_valid():
            occupation = occupation_form.save(commit=False)
            occupation.room = room
            occupation.save()
            room.is_occupied = True
            room.save()
            return redirect('room_details', id=id)

        # If the request is from an agent to add a bill
        bill_form = BillForm(request.POST)
        if bill_form.is_valid():
            bill = bill_form.save(commit=False)
            bill.room = room
            bill.tenant = occupation.first().tenant
            bill.save()
            messages.success(request, f'Bill created successfully')
            return redirect('room_details', id=id)

    if request.method == 'POST' and is_authenticated_tenant:
        # If the request is from a tenant to book a room
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tenant = request.user.tenant
            booking.save()
            messages.success(request, f'Booking created successfully')
            return redirect('room_details', id=id)

    context = {
        'room': room,
        'available_times': available_times,
        'form': form if is_authenticated_tenant else None,
        'is_authenticated_tenant': is_authenticated_tenant,
        'has_booking': has_booking,
        'booking': booking,
        'occupation_form': occupation_form,
        'occupation': occupation,
        'bill_form': bill_form,
        'bills': bills,
    }
    return render(request, 'users/room_details.html', context)


def add_available_time(request, id):
    user = request.user
    room = Room.objects.get(id=id)
    if request.method == 'POST':
        form = AvailableTimeForm(request.POST)
        if form.is_valid():
            available_time = form.save(commit=False)
            available_time.agent = user.agent
            available_time.room = room
            form.save()
            messages.success(request, f'Available time created successfully')
            return redirect('room_details', id=id)
    else:
        messages.error(request, f'Error creating available time')
        form = AvailableTimeForm()

    return render(request, 'users/add_available_time.html', {'form': form})

# def show_available_time(request, id):
#     room = Room.objects.get(id=id)
#     available_times = AvailableTime.objects.filter(room=room)
#     context = {
#         'available_times': available_times,
#     }
#     return render(request, 'users/show_available_time.html', context)


def add_booking(request, room_id):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room_id = room_id

            # Check for conflicting bookings for the selected time slot
            conflicting_bookings = Booking.objects.filter(
                available_time=booking.available_time,
                room_id=room_id
            )

            if conflicting_bookings.exists():
                messages.error(
                    request, "This room is already booked for the selected time slot.")
            else:
                form.save()
                return redirect('room_details', id=room_id)
    else:
        form = BookingForm()

    return render(request, 'users/add_booking.html', {'form': form})


@login_required
def cancel_booking(request, id):
    booking = get_object_or_404(Booking, pk=id)

    if request.method == 'POST':
        booking.delete()
        messages.success(request, f'Booking cancelled successfully')
        return redirect('room_details', id=booking.available_time.room.id)

    return render(request, 'users/cancel_booking.html', {'booking': booking})


@login_required
def remove_occupation(request, id):
    if request.method == 'POST' and request.user.is_agent:
        occupation = get_object_or_404(Occupation, pk=id)
        room = occupation.room
        occupation.delete()
        room.is_occupied = False
        room.save()
        messages.success(request, f'Occupant removed successfully')
    return redirect('room_details', id=room.id)


@login_required
def make_payment(request):
    tenant = request.user.tenant
    bills = Bill.objects.filter(tenant=tenant)

    if request.method == 'POST':
        # Handle payment logic here (e.g., update payment status, save payment info, etc.)

        # Example: Setting all bills as paid
        for bill in bills:
            bill.is_paid = True
            bill.save()

        # Redirect to a success page or any relevant page
        messages.success(request, f'Payment made successfully')
        return redirect('tenant_home')

    context = {
        'bills': bills,
    }
    return render(request, 'users/make_payment.html', context)


@login_required
@agent_required
def add_occupation(request, room_id):
    if request.method == 'POST':
        form = OccupationForm(request.POST)
        if form.is_valid():
            occupation = form.save(commit=False)
            room = Room.objects.get(id=room_id)
            occupation.room = room
            occupation.save()
            room.is_occupied = True
            room.save()

            contract = Contract.objects.create(
                tenant=occupation.tenant,
                room=room,
                start_date=occupation.start_date,
                agent_first_name=request.user.first_name,  # Set the agent's first name
                agent_last_name=request.user.last_name,    # Set the agent's last name
                tenant_first_name=occupation.tenant.first_name,  # Set the tenant's first name
                tenant_last_name=occupation.tenant.last_name,    # Set the tenant's last name
            )
            messages.success(request, f'Occupant added successfully')
            return redirect('room_details', id=room_id)
    else:
        form = OccupationForm()

    return render(request, 'users/add_occupation.html', {'form': form})


@login_required
@agent_required
def add_bill(request, room_id):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            room = Room.objects.get(id=room_id)
            bill.room = room
            # Set the tenant based on the room's occupation
            occupation = Occupation.objects.filter(room=room).first()
            bill.tenant = occupation.tenant if occupation else None
            bill.save()
            return redirect('room_details', id=room_id)
    else:
        form = BillForm()

    return render(request, 'users/add_bill.html', {'form': form})


@login_required
@agent_required
def add_room(request, pk):
    apartment = Apartment.objects.get(pk=pk)
    print(apartment)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.apartment = apartment
            room.save()
            return redirect('property_details', id=pk)
    else:
        form = RoomForm()

    return render(request, 'users/add_room.html', {'form': form})


@login_required
@agent_required
def update_room(request, pk):
    room = Room.objects.get(pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('property_details', id=room.apartment.id)
    else:
        form = RoomForm(instance=room)

    return render(request, 'users/add_room.html', {'form': form})


@login_required
@agent_required
def delete_room(request, pk):
    room = Room.objects.get(pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('property_details', id=room.apartment.id)
    return render(request, 'users/delete_room.html', {'room': room})


def listings(request):
    apartments = Apartment.objects.all()
    context = {
        'apartments': apartments,
    }
    return render(request, 'users/listings.html', context)


@login_required
@agent_required
def update_apartment(request, pk):
    apartment = Apartment.objects.get(pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=apartment)
        if form.is_valid():
            form.save()
            return redirect('property_details', id=pk)
    else:
        form = PropertyForm(instance=apartment)

    return render(request, 'users/create_property.html', {'form': form})


@login_required
@agent_required
def delete_apartment(request, pk):
    apartment = Apartment.objects.get(pk=pk)
    if request.method == 'POST':
        apartment.delete()
        messages.success(request, f'Apartment deleted successfully')
        return redirect('listings')
    return render(request, 'users/delete_apartment.html', {'apartment': apartment})


@login_required
@agent_required
def deleteBill(request, pk):
    bill = Bill.objects.get(pk=pk)
    if request.method == 'POST':
        bill.delete()
        messages.success(request, f'Bill deleted successfully')
        return redirect('room_details', id=bill.room.id)
    return render(request, 'users/delete_bill.html', {'bill': bill})


def logout_view(request):
    logout(request)
    return redirect('landing_page')
