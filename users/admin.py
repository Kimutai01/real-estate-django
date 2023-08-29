from django.contrib import admin

# Register your models here.
from .models import User, Agent, Tenant, Apartment, Room, Booking, AvailableTime, Occupation, Contract

admin.site.register(User)
admin.site.register(Agent)
admin.site.register(Tenant)
admin.site.register(Apartment)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(AvailableTime)
admin.site.register(Occupation)
admin.site.register(Contract)
