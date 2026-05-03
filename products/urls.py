# products/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', product_list, name='product_list'),
    path('add/', add_product, name='add_product'),
 
path('edit/<int:pk>/', edit_product, name='edit_product'),
path('delete/<int:pk>/', delete_product, name='delete_product'),
    path('categories/add/', add_category, name='add_category'),
    # products/urls.py
    path('stock/<int:pk>/', update_stock, name='update_stock'),
path('categories/', category_list, name='category_list'),
]