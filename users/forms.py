from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.db import transaction
from .models import User,Agent,Tenant,Property,Room,Booking
from django import forms
from django.contrib.auth import get_user_model

class AgentSignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    id_number = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput())
    

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','email','password1','password2')
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_agent = True
        if commit:
            user.save()
        agent = Agent.objects.create(user=user,first_name=self.cleaned_data.get('first_name'),last_name=self.cleaned_data.get('last_name'),id_number=self.cleaned_data.get('id_number'))
        return user
    
class TenantSignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    id_number = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput())
    

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','email','password1','password2')
    
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
        fields = ('name','location','price','description')
        
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('name','property')
        
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('tenant','room','check_in','check_out')