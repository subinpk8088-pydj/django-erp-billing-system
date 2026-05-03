from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.views import admin_required
from .models import Product
from .forms import ProductForm


@login_required
def product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'products/product_list.html', {'products': products})


@login_required
@admin_required
def add_product(request):
    form = ProductForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('product_list')

    return render(request, 'products/product_form.html', {'form': form})


@login_required
@admin_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)

    if form.is_valid():
        form.save()
        return redirect('product_list')

    return render(request, 'products/product_form.html', {'form': form})


@login_required
@admin_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')

    return render(request, 'products/product_confirm_delete.html', {'product': product})
# products/views.py

from .models import Category
from django.shortcuts import render, redirect

@login_required
@admin_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('category_list')

    return render(request, 'products/category_form.html')

# products/views.py

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {
        'categories': categories
    })
    
    
    
@login_required
@admin_required
def update_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))

        product.stock += quantity  # add stock
        product.save()

        return redirect('product_list')

    return render(request, 'products/update_stock.html', {'product': product})    