from django.urls import path
from .views import *

urlpatterns = [

    path(
        '',
        payment_list,
        name='payment_list'
    ),

    path(
        'create/',
        create_payment,
        name='create_payment'
    ),

    path(
        '<int:pk>/',
        payment_detail,
        name='payment_detail'
    ),

    # AJAX
    path(
        'invoice-details/<int:invoice_id>/',
        invoice_details_api,
        name='invoice_details_api'
    ),
]