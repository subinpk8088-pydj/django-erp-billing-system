from django.urls import path

from .views import *


urlpatterns = [

    path(
        '',
        purchase_list,
        name='purchase_list'
    ),

    path(
        'create/',
        create_purchase,
        name='create_purchase'
    ),

    path(
        '<int:pk>/',
        purchase_detail,
        name='purchase_detail'
    ),
]