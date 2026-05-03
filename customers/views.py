# customers/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from accounts.views import admin_required
from .models import Customer
from .forms import CustomerForm


@login_required
def customer_list(request):
    search_query = request.GET.get('q', '')

    customers = Customer.objects.all()

    if search_query:
        customers = customers.filter(name__icontains=search_query)

    paginator = Paginator(customers, 5)  # 5 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customers/customer_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


@login_required
@admin_required
def add_customer(request):
    form = CustomerForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('customer_list')

    return render(request, 'customers/customer_form.html', {'form': form})


@login_required
@admin_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('customer_list')

    return render(request, 'customers/customer_form.html', {'form': form})


@login_required
@admin_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')

    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})