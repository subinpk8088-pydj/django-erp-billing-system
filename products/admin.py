from django.contrib import admin

# Register your models here.
# products/admin.py

from django.contrib import admin
from .models import Product, Category

admin.site.register(Product)
admin.site.register(Category)