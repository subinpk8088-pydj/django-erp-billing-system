# accounts/views.py

from functools import wraps
import json

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.decorators import login_required

from django.shortcuts import (
    render,
    redirect
)

from django.http import HttpResponse

from django.contrib import messages

from django.db.models import (
    Sum,
    F
)

from django.db.models.functions import TruncDate

from invoices.models import Invoice
from products.models import Product

from .forms import UserRegisterForm

from accounts.decorators import (
    admin_required,
    accountant_required
)


# ==========================================
# LOGIN
# ==========================================
def login_view(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        # =================================
        # BASIC VALIDATION
        # =================================

        if not username or not password:

            return render(
                request,
                'accounts/login.html',
                {
                    'error': 'Username and password are required'
                }
            )

        # =================================
        # AUTHENTICATE USER
        # =================================

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # =================================
            # SUPERUSER ALWAYS ADMIN
            # =================================

            if user.is_superuser:

                return redirect(
                    'admin_dashboard'
                )

            # =================================
            # ROLE BASED REDIRECTION
            # =================================

            elif user.role == 'admin':

                return redirect(
                    'admin_dashboard'
                )

            elif user.role == 'accountant':

                return redirect(
                    'accountant_dashboard'
                )

            elif user.role == 'staff':

                return redirect(
                    'staff_dashboard'
                )

            # =================================
            # INVALID ROLE
            # =================================

            else:

                logout(request)

                return render(
                    request,
                    'accounts/login.html',
                    {
                        'error': 'Invalid role assigned'
                    }
                )

        # =================================
        # INVALID LOGIN
        # =================================

        else:

            return render(
                request,
                'accounts/login.html',
                {
                    'error': 'Invalid username or password'
                }
            )

    return render(
        request,
        'accounts/login.html'
    )

# ==========================================
# LOGOUT
# ==========================================

def logout_view(request):

    logout(request)

    return redirect(
        'login'
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

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

    # =================================
    # SALES TREND
    # =================================

    sales_data = (

        Invoice.objects

        .annotate(
            day=TruncDate('date')
        )

        .values('day')

        .annotate(
            total=Sum('grand_total')
        )

        .order_by('day')

    )

    dates = [
        str(item['day'])
        for item in sales_data
    ]

    totals = [
        float(item['total'])
        for item in sales_data
    ]

    context = {

        'total_invoices': total_invoices,

        'total_revenue': total_revenue,

        'total_products': total_products,

        'low_stock_count': low_stock_products.count(),

        'low_stock_products': low_stock_products,

        'dates': json.dumps(dates),

        'totals': json.dumps(totals),
    }

    return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )


# ==========================================
# STAFF DASHBOARD
# ==========================================

@login_required
def staff_dashboard(request):

    return render(
        request,
        'accounts/staff_dashboard.html'
    )


# ==========================================
# ACCOUNTANT DASHBOARD
# ==========================================

@login_required
@accountant_required
def accountant_dashboard(request):

    return render(
        request,
        'accounts/accountant_dashboard.html'
    )


# ==========================================
# REGISTER USER
# ==========================================

@login_required
@admin_required
def register_user(request):

    form = UserRegisterForm(
        request.POST or None
    )

    # =================================
    # SECURITY:
    # DO NOT ALLOW ADMIN CREATION
    # =================================

    form.fields['role'].choices = [

        ('staff', 'Staff'),

        ('accountant', 'Accountant')

    ]

    if request.method == 'POST':

        if form.is_valid():

            user = form.save(
                commit=False
            )

            # ensure no privilege escalation
            if user.role == 'admin':

                messages.error(
                    request,
                    "Admin creation not allowed"
                )

                return redirect(
                    'register_user'
                )

            user.save()

            messages.success(
                request,
                "User created successfully"
            )

            return redirect(
                'admin_dashboard'
            )

    return render(

        request,

        'accounts/register_user.html',

        {
            'form': form
        }
    )