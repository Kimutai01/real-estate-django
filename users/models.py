from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_agent = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)
    
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    id_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.first_name + " " + self.last_name
    
class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12, null=True)
    id_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.first_name + " " + self.last_name
    
class Property(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    image = models.ImageField(default='default.jpg', blank=True, null=True, upload_to='apartments')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
class Room(models.Model):
    name = models.CharField(max_length=50)
    apartment = models.ForeignKey(Property, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField(default=0)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True)
    
    @property
    def is_occupied(self) -> bool:
        return self.tenant != None
    
    def __str__(self):
        return self.name

class AvailableTime(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    def __str__(self):
        return self.date.strftime("%Y-%m-%d") + " " + self.time.strftime("%H:%M:%S")
    
class Booking(models.Model):
    available_time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.available_time.agent.first_name} {self.available_time.agent.last_name} {self.available_time.room.name} {self.tenant.first_name} {self.tenant.last_name}"
    

class Occupation(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    def __str__(self):
        return self.tenant.first_name + self.room.name
    
def create_occupation(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        room.is_occupied = True
        room.save()
        
models.signals.post_save.connect(create_occupation, sender=Occupation)

def delete_occupation(sender, instance, **kwargs):
    room = instance.room
    room.is_occupied = False
    room.save()
    
models.signals.post_delete.connect(delete_occupation, sender=Occupation)

