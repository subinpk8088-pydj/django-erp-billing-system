from django.db import models

# Create your models here.
from django.db import models

from accounts.models import CustomUser


class ExpenseCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):

        return self.name


class Expense(models.Model):

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    expense_date = models.DateField()

    note = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['-expense_date']

    def __str__(self):

        return self.title