from django import forms

from .models import CustomerPayment


class CustomerPaymentForm(forms.ModelForm):

    class Meta:

        model = CustomerPayment

        fields = [

            'invoice',

            'amount',

            'payment_method',

            'reference_number',

            'note'
        ]

        widgets = {

            'note': forms.Textarea(
                attrs={'rows': 3}
            )
        }