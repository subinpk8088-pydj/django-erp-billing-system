# customers/forms.py

from django import forms
from .models import Customer
import re

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = '__all__'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Phone must be 10 digits")

        return phone

    def clean_gst_number(self):
        gst = self.cleaned_data.get('gst_number')

        if gst:
            pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{3}$'
            if not re.match(pattern, gst):
                raise forms.ValidationError("Invalid GST number")

        return gst