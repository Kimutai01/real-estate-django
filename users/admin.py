from django.contrib import admin

# Register your models here.
from .models import User,Agent,Tenant,Property,Room,Booking

admin.site.register(User)
admin.site.register(Agent)
admin.site.register(Tenant)
admin.site.register(Property)
admin.site.register(Room)
admin.site.register(Booking)
