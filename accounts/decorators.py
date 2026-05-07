from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def admin_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        # 🔥 superuser bypass
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # 🔥 custom role check
        if request.user.role != 'admin':
            return HttpResponseForbidden(
                "Admin access required"
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def staff_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'staff':
            return HttpResponseForbidden(
                "Staff access required"
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def accountant_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'accountant':
            return HttpResponseForbidden(
                "Accountant access required"
            )

        return view_func(request, *args, **kwargs)

    return wrapper