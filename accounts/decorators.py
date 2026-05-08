from functools import wraps

from django.shortcuts import redirect

from django.http import HttpResponseForbidden


def role_required(allowed_roles):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # 🔥 authentication check
            if not request.user.is_authenticated:

                return redirect('login')

            # 🔥 superuser bypass
            if request.user.is_superuser:

                return view_func(
                    request,
                    *args,
                    **kwargs
                )

            # 🔥 role check
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


# 🔥 ADMIN ONLY
admin_required = role_required([
    'admin'
])


# 🔥 STAFF ONLY
staff_required = role_required([
    'staff'
])


# 🔥 ACCOUNTANT + ADMIN
accountant_required = role_required([
    'admin',
    'accountant'
])