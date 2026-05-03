# customers/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', customer_list, name='customer_list'),
    path('add/', add_customer, name='add_customer'),
    path('edit/<int:pk>/', edit_customer, name='edit_customer'),
    path('delete/<int:pk>/', delete_customer, name='delete_customer'),
]