# accounts/views.py

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# ------------------------
# LOGIN
# ------------------------
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # basic validation (don't trust empty input)
        if not username or not password:
            return render(request, 'accounts/login.html', {
                'error': 'Username and password are required'
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ✅ correct priority logic
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role == 'accountant':
                return redirect('accountant_dashboard')
            elif user.role == 'staff':
                return redirect('staff_dashboard')
            else:
                # fallback (in case role is empty or corrupted)
                return redirect('staff_dashboard')

        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'accounts/login.html')
# ------------------------
# LOGOUT
# ------------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------------
# ROLE CHECK DECORATORS
# ------------------------
from functools import wraps
from django.http import HttpResponse

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized", status=401)

        # allow superuser OR role admin
        if not (request.user.is_superuser or request.user.role == 'admin'):
            return HttpResponse("Unauthorized", status=401)

        return view_func(request, *args, **kwargs)
    return wrapper


def accountant_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'accountant':
            return HttpResponse("Unauthorized", status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


# ------------------------
# DASHBOARDS
# ------------------------
from django.db.models.functions import TruncDate
from django.db.models import Sum
import json
from invoices.models import Invoice
from products.models import Product
from django.db.models import Sum, F
@login_required
@admin_required
def admin_dashboard(request):

    total_invoices = Invoice.objects.count()

    total_revenue = Invoice.objects.aggregate(
        total=Sum('grand_total')
    )['total'] or 0

    total_products = Product.objects.count()

    low_stock_products = Product.objects.filter(
        stock__lte=F('low_stock_threshold')
    )

    # 🔥 SALES TREND (last 7 days)
    sales_data = (
        Invoice.objects
        .annotate(day=TruncDate('date'))
        .values('date')
        .annotate(total=Sum('grand_total'))
        .order_by('date')
    )

    dates = [str(item['date']) for item in sales_data]
    totals = [float(item['total']) for item in sales_data]

    context = {
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products,

        # 🔥 chart data
        'dates': json.dumps(dates),
        'totals': json.dumps(totals),
    }

    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def staff_dashboard(request):
    return render(request, 'accounts/staff_dashboard.html')


@login_required
@accountant_required
def accountant_dashboard(request):
    return render(request, 'accounts/accountant_dashboard.html')