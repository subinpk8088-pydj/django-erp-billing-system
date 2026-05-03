from django.contrib import admin

# Register your models here.
# customers/admin.py

from django.contrib import admin
from .models import Customer

admin.site.register(Customer)