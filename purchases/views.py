# purchases/views.py

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

from inventory.utils import create_stock_movement

from .models import Purchase, PurchaseItem

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

    form = PurchaseForm(request.POST or None)

    formset = PurchaseItemFormSet(request.POST or None)

    if request.method == 'POST':

        if form.is_valid() and formset.is_valid():

            try:

                with transaction.atomic():

                    purchase = form.save(commit=False)

                    purchase.created_by = request.user

                    purchase.save()

                    items = formset.save(commit=False)

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

                        product = item.product

                        stock_before = product.stock

                        product.stock += item.quantity

                        stock_after = product.stock

                        product.save()

                        create_stock_movement(

                            product=product,

                            movement_type='PURCHASE',

                            quantity=item.quantity,

                            stock_before=stock_before,

                            stock_after=stock_after,

                            user=request.user,

                            reference=purchase.invoice_number,

                            note='Purchase created'
                        )

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


@login_required
@admin_required
def edit_purchase(request, pk):

    purchase = get_object_or_404(
        Purchase,
        pk=pk
    )

    form = PurchaseForm(
        request.POST or None,
        instance=purchase
    )

    formset = PurchaseItemFormSet(
        request.POST or None,
        instance=purchase
    )

    if request.method == 'POST':

        if form.is_valid() and formset.is_valid():

            try:

                with transaction.atomic():

                    old_items = PurchaseItem.objects.filter(
                        purchase=purchase
                    )

                    for old_item in old_items:

                        product = old_item.product

                        stock_before = product.stock

                        product.stock -= old_item.quantity

                        stock_after = product.stock

                        product.save()

                        create_stock_movement(

                            product=product,

                            movement_type='PURCHASE_EDIT',

                            quantity=-old_item.quantity,

                            stock_before=stock_before,

                            stock_after=stock_after,

                            user=request.user,

                            reference=purchase.invoice_number,

                            note='Purchase rollback during edit'
                        )

                    old_items.delete()

                    purchase = form.save(
                        commit=False
                    )

                    purchase.save()

                    items = formset.save(
                        commit=False
                    )

                    total = Decimal('0.00')

                    for item in items:

                        item.purchase = purchase

                        item.save()

                        product = item.product

                        stock_before = product.stock

                        product.stock += item.quantity

                        stock_after = product.stock

                        product.save()

                        create_stock_movement(

                            product=product,

                            movement_type='PURCHASE_EDIT',

                            quantity=item.quantity,

                            stock_before=stock_before,

                            stock_after=stock_after,

                            user=request.user,

                            reference=purchase.invoice_number,

                            note='Purchase updated'
                        )

                        total += (
                            item.quantity *
                            item.purchase_price
                        )

                    purchase.total_amount = total

                    purchase.save()

                    messages.success(
                        request,
                        "Purchase updated successfully"
                    )

                    return redirect(
                        'purchase_list'
                    )

            except Exception as e:

                print(e)

                messages.error(
                    request,
                    "Purchase update failed"
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
def delete_purchase(request, pk):

    purchase = get_object_or_404(
        Purchase,
        pk=pk
    )

    if request.method == 'POST':

        try:

            with transaction.atomic():

                items = PurchaseItem.objects.filter(
                    purchase=purchase
                )

                for item in items:

                    product = item.product

                    stock_before = product.stock

                    product.stock -= item.quantity

                    stock_after = product.stock

                    product.save()

                    create_stock_movement(

                        product=product,

                        movement_type='PURCHASE_DELETE',

                        quantity=-item.quantity,

                        stock_before=stock_before,

                        stock_after=stock_after,

                        user=request.user,

                        reference=purchase.invoice_number,

                        note='Purchase deleted rollback'
                    )

                purchase.delete()

                messages.success(
                    request,
                    "Purchase deleted successfully"
                )

                return redirect(
                    'purchase_list'
                )

        except Exception as e:

            print(e)

            messages.error(
                request,
                "Purchase delete failed"
            )

    return render(
        request,
        'purchases/delete_purchase.html',
        {
            'purchase': purchase
        }
    )