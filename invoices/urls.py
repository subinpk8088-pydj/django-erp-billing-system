# invoices/urls.py

from django.urls import path
from .views import *

urlpatterns = [
path('', invoice_list, name='invoice_list'),
path('create/', create_invoice, name='create_invoice'),
# invoices/urls.py

path('<int:pk>/', invoice_detail, name='invoice_detail'),
path('<int:pk>/paid/', mark_paid, name='mark_paid'),
path('<int:pk>/pdf/', invoice_pdf, name='invoice_pdf'),
]