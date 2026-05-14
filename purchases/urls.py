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

    path(
        'edit/<int:pk>/',
        edit_purchase,
        name='edit_purchase'
    ),

    path(
        'delete/<int:pk>/',
        delete_purchase,
        name='delete_purchase'
    ),

    # AJAX
    path(
        'ajax/product-price/',
        get_product_price,
        name='get_product_price'
    ),

]