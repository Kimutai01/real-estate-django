from uuid import uuid4
from django.db import models

class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-updated_at', ]


class Bill(TimestampModel):
    tenant = models.ForeignKey('users.Tenant', on_delete=models.CASCADE)
    room = models.ForeignKey('users.Room', on_delete=models.CASCADE)
    invoice_no = models.UUIDField(default=uuid4, unique=True)
    extra_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(null=True)
    due_date = models.DateField()

    
    def __str__(self):
        return self.tenant.first_name + self.room.name
    
    @property
    def amount(self):
        return self.extra_amount + self.room.price    


class Payment(TimestampModel):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    merchent_id = models.CharField(null=True, max_length=128)
    checkout_id = models.CharField(null=True, max_length=128)
    is_complete = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)