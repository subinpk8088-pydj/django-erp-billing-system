from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from functools import wraps


def role_required(allowed_roles):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect('login')

            # SUPERUSER BYPASS
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # ROLE CHECK
            if request.user.role not in allowed_roles:

                return HttpResponseForbidden(
                    "Permission denied"
                )

            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator


# ADMIN ONLY
def admin_required(view_func):
    return role_required(
        ['admin']
    )(view_func)


# ACCOUNTANT + ADMIN
def accountant_required(view_func):
    return role_required(
        ['admin', 'accountant']
    )(view_func)


# STAFF + ADMIN + ACCOUNTANT
def staff_required(view_func):
    return role_required(
        ['admin', 'accountant', 'staff']
    )(view_func)