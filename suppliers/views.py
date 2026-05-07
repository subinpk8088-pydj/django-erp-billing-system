from django.shortcuts import render

# Create your views here.
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from accounts.decorators import admin_required

from .models import Supplier
from .forms import SupplierForm


@login_required
@admin_required
def supplier_list(request):

    suppliers = Supplier.objects.all().order_by('-id')

    return render(
        request,
        'suppliers/supplier_list.html',
        {
            'suppliers': suppliers
        }
    )


@login_required
@admin_required
def add_supplier(request):

    form = SupplierForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect('supplier_list')

    return render(
        request,
        'suppliers/add_supplier.html',
        {
            'form': form
        }
    )


@login_required
@admin_required
def edit_supplier(request, pk):

    supplier = get_object_or_404(
        Supplier,
        pk=pk
    )

    form = SupplierForm(
        request.POST or None,
        instance=supplier
    )

    if form.is_valid():

        form.save()

        return redirect('supplier_list')

    return render(
        request,
        'suppliers/add_supplier.html',
        {
            'form': form
        }
    )


@login_required
@admin_required
def delete_supplier(request, pk):

    supplier = get_object_or_404(
        Supplier,
        pk=pk
    )

    if request.method == 'POST':

        supplier.delete()

        return redirect('supplier_list')

    return render(
        request,
        'suppliers/delete_supplier.html',
        {
            'supplier': supplier
        }
    )