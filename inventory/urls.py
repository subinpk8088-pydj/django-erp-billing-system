# inventory/urls.py

from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.stock_movement_list,
        name='stock_movement_list'
    ),

]