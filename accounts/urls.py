# accounts/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login'),

    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', staff_dashboard, name='staff_dashboard'),
    path('accountant-dashboard/', accountant_dashboard, name='accountant_dashboard'),

    path('logout/', logout_view, name='logout'),
]