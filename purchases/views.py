from django.shortcuts import render

# Create your views here.
from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.db import transaction

from accounts.decorators import admin_required

from .models import Purchase

from .forms import (
    PurchaseForm,
    PurchaseItemFormSet
)


@login_required
@admin_required
def purchase_list(request):

    purchases = Purchase.objects.all().order_by('-id')

    return render(
        request,
        'purchases/purchase_list.html',
        {
            'purchases': purchases
        }
    )


@login_required
@admin_required
def create_purchase(request):

    form = PurchaseForm(
        request.POST or None
    )

    formset = PurchaseItemFormSet(
        request.POST or None
    )

    if request.method == 'POST':

        if form.is_valid() and formset.is_valid():

            try:

                with transaction.atomic():

                    purchase = form.save(
                        commit=False
                    )

                    purchase.created_by = request.user

                    purchase.save()

                    items = formset.save(
                        commit=False
                    )

                    total = Decimal('0.00')

                    if not items:

                        messages.error(
                            request,
                            "At least one item required"
                        )

                        raise Exception()

                    for item in items:

                        item.purchase = purchase

                        item.save()

                        # 🔥 STOCK INCREASE
                        product = item.product

                        product.stock += item.quantity

                        product.save()

                        total += (
                            item.quantity *
                            item.purchase_price
                        )

                    purchase.total_amount = total

                    purchase.save()

                    messages.success(
                        request,
                        "Purchase created successfully"
                    )

                    return redirect(
                        'purchase_list'
                    )

            except Exception as e:

                print(e)

                messages.error(
                    request,
                    "Purchase failed"
                )

    return render(
        request,
        'purchases/purchase_form.html',
        {
            'form': form,
            'formset': formset
        }
    )


@login_required
@admin_required
def purchase_detail(request, pk):

    purchase = get_object_or_404(
        Purchase,
        pk=pk
    )

    return render(
        request,
        'purchases/purchase_detail.html',
        {
            'purchase': purchase
        }
    )