from django.shortcuts import render,redirect
from .models import User,Agent,Tenant,Property,Room,Booking
from .forms import AgentSignUpForm,TenantSignUpForm,LoginForm,PropertyForm,RoomForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .decorators import tenant_required,agent_required
from django.http import Http404



# Create your views here.
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
    context = {
        'properties':properties
    }
    return render(request,'users/tenant_home.html',context)

@login_required
@agent_required
def agent_home(request):
    apartment = Property.objects.filter(agent=request.user.agent)
    print(apartment)
    context={'apartment':apartment}
    
    return render(request,'users/agent_home.html',context)

@login_required
def property_details(request, id): 
    apartment = Property.objects.get(id=id)
    rooms = Room.objects.filter(property=apartment)
    context = {
        'apartment': apartment,
        'rooms': rooms
    }
    return render(request, 'users/property_details.html', context)

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
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_instance = form.save(commit=False)
            
            # Set the agent for the property instance before saving
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

@login_required
@agent_required
def create_room(request):
    user = request.user

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room_instance = form.save(commit=False)
            
            # Set the agent for the property instance before saving
            try:
                agent = get_object_or_404(Agent, user=user)
                room_instance.agent = agent
                room_instance.save()
                return redirect('agent_home')
            except IntegrityError:
             
                return HttpResponseServerError("Agent not found for the user.")
    else:
        form = RoomForm()

    return render(request, 'users/create_room.html', {'form': form})
