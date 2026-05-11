from django.urls import path
from .views import *

urlpatterns = [

    # =========================================
    # EXPENSES
    # =========================================

    path(
        '',
        expense_list,
        name='expense_list'
    ),

    path(
        'create/',
        create_expense,
        name='create_expense'
    ),

    path(
        'delete/<int:pk>/',
        delete_expense,
        name='delete_expense'
    ),

    # =========================================
    # EXPENSE CATEGORIES
    # =========================================

    path(
        'categories/',
        category_list,
        name='expense_category_list'
    ),

    path(
        'categories/create/',
        create_category,
        name='create_expense_category'
    ),

]