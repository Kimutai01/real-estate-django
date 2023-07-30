from django.shortcuts import render,redirect, get_object_or_404
from .models import User,Agent,Tenant,Property,Room,Booking
from .forms import AgentSignUpForm,TenantSignUpForm,LoginForm,PropertyForm,RoomForm, BookingForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .decorators import tenant_required,agent_required
from django.http import Http404
from django.shortcuts import render
from .models import Property, Booking


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
    print(bookings)
    context = {
        'properties':properties,
        'bookings':bookings
    }
    return render(request,'users/tenant_home.html',context)

@login_required
@agent_required
def agent_home(request):
    apartment = Property.objects.filter(agent=request.user.agent)
    print(apartment)
    context={'apartment':apartment}
    
    return render(request,'users/agent_home.html',context)

def property_details(request, id): 
    apartment = Property.objects.get(id=id)
    rooms = Room.objects.filter(property=apartment)

    context = {
        'apartment': apartment,
        'rooms': rooms,
        'property_id': id,
    }
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.property = apartment
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
    context = {
        'room': room,
    }
    return render(request, 'users/room_details.html', context)


@login_required
def book_room(request, id):
    user = request.user
    room = Room.objects.get(id=id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']

            # Check for conflicting bookings
            conflicting_bookings = Booking.objects.filter(room=room, check_out__gt=check_in, check_in__lt=check_out)

            if conflicting_bookings.exists():
                form.add_error(None, "This room is already booked for the selected time slot.")
            else:
                booking = form.save(commit=False)
                booking.room = room
                booking.tenant = request.user.tenant
                form.save()
                return redirect('room_details', id=id)
    else:
        form = BookingForm()

    return render(request, 'users/book_room.html', {'form': form})


@login_required
def cancel_booking(request, id):
    room = get_object_or_404(Room, pk=id)
    bookings = Booking.objects.filter(room=room, tenant=request.user.tenant)

    if bookings.exists():
        # If there are multiple bookings for the same user and room, just delete the first one
        booking_to_cancel = bookings.first()
        booking_to_cancel.delete()
        return redirect('booking', id=id)
    else:
        # Handle the case where no booking exists
        return redirect('booking', id=id)
