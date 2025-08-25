from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('apply/', views.apply_now, name='apply_now'),
    path('success/<int:applicant_id>/', views.application_success, name='application_success'),
]