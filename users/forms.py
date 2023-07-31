from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.db import transaction
from .models import User,Agent,Tenant,Property,Room,Booking
from django import forms
from tempus_dominus.widgets import DatePicker
from django.contrib.auth import get_user_model

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
        tenant = Tenant.objects.create(user=user,first_name=self.cleaned_data.get('first_name'),last_name=self.cleaned_data.get('last_name'),id_number=self.cleaned_data.get('id_number'))
        return user
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
        
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ('agent',)
        fields = ('name','location','image','price','description')
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'image': forms.FileInput(attrs={'class': 'w-full'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring focus:border-blue-500'}),
            'agent': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring focus:border-blue-500'}),
        }
        
        
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ('property',)
        fields=('name',)
        
class BookingForm(forms.ModelForm):
    widget = {
        'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    class Meta:
        model = Booking
        exclude = ('tenant', 'room')
        fields = ('check_in', 'check_out')
        widgets = {
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }