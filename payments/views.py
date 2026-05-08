from django.shortcuts import render

# Create your views here.
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from decimal import Decimal

from accounts.decorators import accountant_required

from invoices.models import Invoice

from .models import CustomerPayment

from .forms import CustomerPaymentForm


@login_required
@accountant_required
def payment_list(request):

    payments = CustomerPayment.objects.select_related(
        'invoice',
        'received_by'
    )

    return render(

        request,

        'payments/payment_list.html',

        {
            'payments': payments
        }
    )


@login_required
@accountant_required
def create_payment(request):

    form = CustomerPaymentForm(
        request.POST or None
    )

    if request.method == 'POST':

        if form.is_valid():

            payment = form.save(
                commit=False
            )

            invoice = payment.invoice

            # 🔥 OVERPAYMENT PROTECTION
            if payment.amount > invoice.balance_due:

                messages.error(

                    request,

                    "Payment exceeds balance due"
                )

                return redirect(
                    'create_payment'
                )

            payment.received_by = request.user

            payment.save()

            # 🔥 UPDATE STATUS
            invoice.update_payment_status()

            messages.success(

                request,

                "Payment added successfully"
            )

            return redirect(
                'payment_list'
            )

    return render(

        request,

        'payments/payment_form.html',

        {
            'form': form
        }
    )


@login_required
@accountant_required
def payment_detail(request, pk):

    payment = get_object_or_404(

        CustomerPayment,

        pk=pk
    )

    return render(

        request,

        'payments/payment_detail.html',

        {
            'payment': payment
        }
    )