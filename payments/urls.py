from django.urls import path
from . import views

urlpatterns = [
    path('payment/', views.payment_gateway, name='payment_gateway'),
    path('payment/verify/', views.verify_payment_view, name='verify_payment'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
]