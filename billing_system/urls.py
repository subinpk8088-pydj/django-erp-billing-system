from django.contrib import admin
from django.urls import path, include



from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # your system entry point
    path('', include('accounts.urls')),
    path('customers/', include('customers.urls')),
    path('products/', include('products.urls')),
    path('invoices/', include('invoices.urls')),
    path('suppliers/',include('suppliers.urls')),
    path('purchases/',include('purchases.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)