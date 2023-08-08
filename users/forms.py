from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.db import transaction
from .models import User,Agent,Tenant,Apartment,Room,Booking,AvailableTime, Occupation
from payments.models import Bill
from django import forms
from tempus_dominus.widgets import DatePicker
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

class AgentSignUpForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your first name',
        }),
        label='First Name'
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your last name',
        }),
        label='Last Name'
    )

    id_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your ID number',
        }),
        label='ID Number'
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your email address',
        }),
        label='Email'
    )

    

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','email','password1','password2')
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
                'placeholder': 'Enter your username',
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
                'placeholder': 'Enter your password',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
                'placeholder': 'Confirm your password',
            }),
        }
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_agent = True
        if commit:
            user.save()
        agent = Agent.objects.create(user=user,first_name=self.cleaned_data.get('first_name'),last_name=self.cleaned_data.get('last_name'),id_number=self.cleaned_data.get('id_number'))
        return user
    
class TenantSignUpForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your first name',
        }),
        label='First Name'
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your last name',
        }),
        label='Last Name'
    )

    id_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your ID number',
        }),
        label='ID Number'
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your email address',
        }),
        label='Email'
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Enter your phone number 254700000000',
        }),
        label='Phone Number'
    )

    

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','email','password1','password2')
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500','placeholder': 'Enter your username'}),
            'password1': forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500','placeholder': 'Enter your password'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500','placeholder': 'Confirm your password'}),
        }
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_tenant = True
        if commit:
            user.save()
        tenant = Tenant.objects.create(user=user,first_name=self.cleaned_data.get('first_name'),last_name=self.cleaned_data.get('last_name'),id_number=self.cleaned_data.get('id_number'),phone_number=self.cleaned_data.get('phone_number'))
        return user
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
        
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Apartment
        exclude = ('agent',)
        fields = ('name','location','image','price','description','street_1','street_2', 'zip_code','city','county')
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'image': forms.FileInput(attrs={'class': 'w-full'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'agent': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring focus:border-blue-500'}),
            'street_1': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'street_2': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'zip_code': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'county': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            
        }
        
        
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ('apartment',)
        fields=('name', 'price', 'description', 'image')
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'image': forms.FileInput(attrs={'class': 'w-full'}),
            'apartment': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring focus:border-blue-500'}),
        }
        

class AvailableTimeForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Select a date',
            'type': 'date',  # This attribute will enable date picker in modern browsers
        }),
        label='Date'
    )

    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Select a time',
            'type': 'time',  # This attribute will enable time picker in modern browsers
        }),
        label='Time'
    )

    class Meta:
        model = AvailableTime
        exclude = ['agent', 'room']
        
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['available_time', ]

        widgets = {
            'available_time': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500'}),
            'tenant': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        room_id = kwargs.pop('room_id', None)
        super().__init__(*args, **kwargs)
        # Filter available times for the specific room
        if room_id is not None:
            self.fields['available_time'].queryset = AvailableTime.objects.filter(room__id=room_id)
            

class OccupationForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Select a date',
            'type': 'date',  # This attribute will enable date picker in modern browsers
        }),
        label='Date'
    )

    class Meta:
        model = Occupation
        exclude = ['room']
        fields = ['tenant', 'start_date']
        
        widgets = {
            'tenant': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500'}),
            'start_date': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500'}),
        }


class BillForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Select a date',
            'type': 'date',  # This attribute will enable date picker in modern browsers
        }),
        
    )
    
    
    class Meta:
        model = Bill
        exclude = ['room', 'tenant']
        fields = [  'extra_amount', 'due_date']
      