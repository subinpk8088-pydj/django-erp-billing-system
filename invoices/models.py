from decimal import Decimal

from django.db import models

from customers.models import Customer
from products.models import Product
from accounts.models import CustomUser


class Invoice(models.Model):

    STATUS_CHOICES = (

        ('paid', 'Paid'),

        ('unpaid', 'Unpaid'),

        ('partial', 'Partial Payment'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    gst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unpaid'
    )

    class Meta:

        ordering = ['-id']

    def __str__(self):

        return f"Invoice #{self.id}"

    # 🔥 TOTAL PAID
    @property
    def total_paid(self):

        return sum(
            payment.amount
            for payment in self.payments.all()
        )

    # 🔥 BALANCE DUE
    @property
    def balance_due(self):

        return self.grand_total - self.total_paid

    # 🔥 AUTO PAYMENT STATUS
    def update_payment_status(self):

        if self.total_paid <= Decimal('0.00'):

            self.status = 'unpaid'

        elif self.total_paid < self.grand_total:

            self.status = 'partial'

        else:

            self.status = 'paid'

        self.save()

    # 🔥 RECALCULATE TOTALS
    def calculate_totals(self):

        subtotal = Decimal('0.00')

        for item in self.items.all():

            subtotal += item.get_total()

        gst = subtotal * Decimal('0.18')

        grand_total = subtotal + gst

        self.total_amount = subtotal
        self.gst_amount = gst
        self.grand_total = grand_total

        self.save()


class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Meta:

        ordering = ['id']

    # 🔥 ITEM TOTAL
    def get_total(self):

        return self.quantity * self.price

    def __str__(self):

        return (
            f"{self.product.name} "
            f"- Invoice #{self.invoice.id}"
        )