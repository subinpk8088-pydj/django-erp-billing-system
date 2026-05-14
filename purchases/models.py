from django.db import models

from suppliers.models import Supplier
from products.models import Product
from accounts.models import CustomUser


# =========================================
# PURCHASE
# =========================================

class Purchase(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='purchases'
    )

    invoice_number = models.CharField(
        max_length=100,
        unique=True
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:

        ordering = ['-id']

    def __str__(self):

        return self.invoice_number


# =========================================
# PURCHASE ITEM
# =========================================

class PurchaseItem(models.Model):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='purchase_items'
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Meta:

        ordering = ['id']

    @property
    def total_price(self):

        return self.quantity * self.purchase_price

    def __str__(self):

        return (
            f"{self.product.name} "
            f"({self.quantity})"
        )