from django.shortcuts import render, HttpResponse
from .services import build_payment_request
from .models import Bill


# Create your views here.

def payment_view(request, pk):
    bill = Bill.objects.get(pk=pk)
    build_payment_request(bill)
    return HttpResponse('We have recieved the payment')
