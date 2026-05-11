from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.db.models import Sum

from accounts.decorators import (
    admin_required,
    accountant_required
)

from .models import (
    Expense,
    ExpenseCategory
)

from .forms import (
    ExpenseForm,
    ExpenseCategoryForm
)


# =========================================
# EXPENSE LIST
# =========================================

@login_required
@accountant_required
def expense_list(request):

    expenses = Expense.objects.select_related(
        'category',
        'created_by'
    ).order_by('-id')

    total_expense = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    return render(

        request,

        'expenses/expense_list.html',

        {
            'expenses': expenses,
            'total_expense': total_expense
        }
    )


# =========================================
# CREATE EXPENSE
# =========================================

@login_required
@accountant_required
def create_expense(request):

    form = ExpenseForm(
        request.POST or None
    )

    if request.method == 'POST':

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.created_by = request.user

            expense.save()

            messages.success(
                request,
                "Expense added successfully"
            )

            return redirect(
                'expense_list'
            )

    return render(

        request,

        'expenses/expense_form.html',

        {
            'form': form
        }
    )


# =========================================
# DELETE EXPENSE
# =========================================

@login_required
@admin_required
def delete_expense(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk
    )

    if request.method == 'POST':

        expense.delete()

        messages.success(
            request,
            "Expense deleted successfully"
        )

        return redirect(
            'expense_list'
        )

    return render(

        request,

        'expenses/delete_expense.html',

        {
            'expense': expense
        }
    )


# =========================================
# CATEGORY LIST
# =========================================

@login_required
@admin_required
def category_list(request):

    categories = ExpenseCategory.objects.all().order_by('-id')

    return render(

        request,

        'expenses/category_list.html',

        {
            'categories': categories
        }
    )


# =========================================
# CREATE CATEGORY
# =========================================

@login_required
@admin_required
@login_required
@admin_required
def create_category(request):

    form = ExpenseCategoryForm(
        request.POST or None
    )

    if request.method == 'POST':

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Expense category added successfully"
            )

            return redirect(
                'expense_category_list'
            )

    return render(

        request,

        'expenses/category_form.html',

        {
            'form': form
        }
    )