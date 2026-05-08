from django import forms

from .models import (
    Expense,
    ExpenseCategory
)


class ExpenseCategoryForm(forms.ModelForm):

    class Meta:

        model = ExpenseCategory

        fields = ['name']


class ExpenseForm(forms.ModelForm):

    class Meta:

        model = Expense

        fields = [

            'category',

            'title',

            'amount',

            'expense_date',

            'note'
        ]

        widgets = {

            'expense_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'note': forms.Textarea(
                attrs={
                    'rows': 3
                }
            )
        }