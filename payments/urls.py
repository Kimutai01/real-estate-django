from django.urls import path

from . import views


urlpatterns = [
    path('pay/<pk>/', views.payment_view, name='stk-push'),
]
