from django import forms

from django.forms import inlineformset_factory

from .models import (
    Purchase,
    PurchaseItem
)


class PurchaseForm(forms.ModelForm):

    class Meta:

        model = Purchase

        fields = [
            'supplier',
            'invoice_number'
        ]

        widgets = {

            'supplier': forms.Select(attrs={
                'class': 'form-control'
            }),

            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }


class PurchaseItemForm(forms.ModelForm):

    class Meta:

        model = PurchaseItem

        fields = [
            'product',
            'quantity',
            'purchase_price'
        ]

        widgets = {

            'product': forms.Select(attrs={
                'class': 'form-control'
            }),

            'quantity': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


PurchaseItemFormSet = inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True
)