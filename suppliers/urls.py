from django.urls import path

from .views import *


urlpatterns = [

    path(
        '',
        supplier_list,
        name='supplier_list'
    ),

    path(
        'add/',
        add_supplier,
        name='add_supplier'
    ),

    path(
        'edit/<int:pk>/',
        edit_supplier,
        name='edit_supplier'
    ),

    path(
        'delete/<int:pk>/',
        delete_supplier,
        name='delete_supplier'
    ),
]