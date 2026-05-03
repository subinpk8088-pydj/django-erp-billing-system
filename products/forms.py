# products/forms.py

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        purchase = cleaned_data.get('purchase_price')
        selling = cleaned_data.get('selling_price')

        if purchase and selling and selling < purchase:
            raise forms.ValidationError("Selling price cannot be less than purchase price")

        return cleaned_data