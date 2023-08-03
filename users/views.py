from django.shortcuts import render,redirect, get_object_or_404
from .models import User,Agent,Tenant,Property,Room,Booking
from .forms import AgentSignUpForm,TenantSignUpForm,LoginForm,PropertyForm,RoomForm,AvailableTimeForm,BookingForm,OccupationForm,BillForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .decorators import tenant_required,agent_required
from django.http import Http404
from django.shortcuts import render
from .models import Property, Booking, AvailableTime, Room, Occupation
from payments.models import Bill
# import messages
from django.contrib import messages
#timezone
from django.utils import timezone
#timedelta
from datetime import timedelta


# Create your views here.
def landing_page(request):
    apartments = Property.objects.all()
    context = {
        'apartments':apartments
    }
    return render(request,'users/home.html',context)
def agent_signup_view(request):
    if request.method == 'POST':
        form = AgentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return render(request,'users/agent_home.html')
    else:
        form = AgentSignUpForm()
    return render(request,'users/agent_signup.html',{'form':form})

def tenant_signup_view(request):
    if request.method == 'POST':
        form = TenantSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return render(request,'users/tenant_home.html')
    else:
        form = TenantSignUpForm()
    return render(request,'users/tenant_signup.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Log the user in
            login(request, form.get_user())
            if request.user.is_agent:
                return redirect('agent_home')
            elif request.user.is_tenant:
                return redirect('tenant_home')

            
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})
 


@login_required
@tenant_required
def tenant_home(request):
    properties = Property.objects.all()
    bookings = Booking.objects.filter(tenant=request.user.tenant)
    occupation = Occupation.objects.filter(tenant=request.user.tenant)
    bills = Bill.objects.filter(tenant=request.user.tenant)

    
    print(bookings)
    print(occupation)
    
    context = {
        'properties':properties,
        'bookings':bookings,
        'bills':bills,
    }
    return render(request,'users/tenant_home.html',context)

@login_required
@agent_required
def agent_home(request):
    apartments = Property.objects.filter(agent=request.user.agent)
    
    # bookings = Booking.objects.filter(room__property__agent=request.user.agent)
    # print(bookings)
    print(apartments)
    context = {
        'apartments': apartments,
        
    }
    return render(request, 'users/agent_home.html', context)

def property_details(request, id): 
    apartment = Property.objects.get(id=id)
    rooms = Room.objects.filter(apartment=apartment)
    print(f"Agent Rooms: {rooms}")
    if request.user.is_tenant:
        rooms = rooms.filter(tenant=None)

    context = {
        'apartment': apartment,
        'rooms': rooms,
        'property_id': id,
    }
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.apartment = apartment
            room.save()
            return redirect('property_details', id=id)
    else:
        form = RoomForm()
    context['form'] = form
    return render(request, 'users/property_details.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing_page')


# @login_required
# @agent_required
# def create_property()
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.http import HttpResponseServerError

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
                return redirect('agent_home')
            except IntegrityError:
             
                return HttpResponseServerError("Agent not found for the user.")
    else:
        form = PropertyForm()

    return render(request, 'users/create_property.html', {'form': form})



def search_results(request):
    search_query = request.GET.get('search_query')
    property_type = request.GET.get('property_type')

    # Filter properties based on search_query and property_type
    properties = Property.objects.filter(
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
    bills = Bill.objects.filter(room=room, tenant=occupation.first().tenant) if occupation else []
    is_authenticated_tenant = request.user.is_authenticated and hasattr(request.user, 'tenant')

    if is_authenticated_tenant:
        booking = Booking.objects.filter(tenant=request.user.tenant, available_time__room=room).first()

    has_booking = Booking.objects.filter(tenant=request.user.tenant, available_time__room=room).exists() if is_authenticated_tenant else False

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
            return redirect('room_details', id=id)

    if request.method == 'POST' and is_authenticated_tenant:
        # If the request is from a tenant to book a room
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tenant = request.user.tenant
            booking.save()
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
            return redirect('agent_home')
    else:
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
                messages.error(request, "This room is already booked for the selected time slot.")
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
        return redirect('tenant_home')

    context = {
        'bills': bills,
        'total_amount': bills.aggregate(Sum('amount'))['amount__sum'] or 0,
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