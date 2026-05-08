from django.db import models

# Create your models here.
from django.db import models

from products.models import Product

from accounts.models import CustomUser


class StockMovement(models.Model):

    MOVEMENT_TYPES = (

        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),

        ('PURCHASE_EDIT', 'Purchase Edit'),
        ('INVOICE_EDIT', 'Invoice Edit'),

        ('PURCHASE_DELETE', 'Purchase Delete'),
        ('INVOICE_DELETE', 'Invoice Delete'),

        ('ADJUSTMENT', 'Adjustment'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    movement_type = models.CharField(
        max_length=50,
        choices=MOVEMENT_TYPES
    )

    quantity = models.IntegerField()

    stock_before = models.IntegerField()

    stock_after = models.IntegerField()

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    note = models.TextField(
        blank=True,
        null=True
    )

    class Meta:

        ordering = ['-created_at']

    def __str__(self):

        return f"{self.product.name} - {self.movement_type}"