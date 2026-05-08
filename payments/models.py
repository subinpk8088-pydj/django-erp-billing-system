from django.db import models

# Create your models here.
from django.db import models

from invoices.models import Invoice

from accounts.models import CustomUser


class CustomerPayment(models.Model):

    PAYMENT_METHODS = (

        ('cash', 'Cash'),

        ('upi', 'UPI'),

        ('bank', 'Bank Transfer'),

        ('card', 'Card'),
    )

    invoice = models.ForeignKey(

        Invoice,

        on_delete=models.CASCADE,

        related_name='payments'
    )

    amount = models.DecimalField(

        max_digits=12,

        decimal_places=2
    )

    payment_method = models.CharField(

        max_length=20,

        choices=PAYMENT_METHODS
    )

    reference_number = models.CharField(

        max_length=100,

        blank=True,

        null=True
    )

    note = models.TextField(

        blank=True,

        null=True
    )

    received_by = models.ForeignKey(

        CustomUser,

        on_delete=models.SET_NULL,

        null=True
    )

    created_at = models.DateTimeField(

        auto_now_add=True
    )

    class Meta:

        ordering = ['-created_at']

    def __str__(self):

        return f"{self.invoice.id} - {self.amount}"