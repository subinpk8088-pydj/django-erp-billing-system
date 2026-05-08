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
]