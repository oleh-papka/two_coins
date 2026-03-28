from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction as db_transaction
from django.db.models import F, Q
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampMixin, StyleMixin


class Currency(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Name")
    symbol = models.CharField(max_length=5, unique=True, verbose_name="Symbol")
    abbr = models.CharField(max_length=5, unique=True, verbose_name="Abbreviation")

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.name} ({self.abbr})"


class Account(TimeStampMixin, StyleMixin):
    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Name")
    balance = models.DecimalField(null=False,
                                  blank=False,
                                  max_digits=10,
                                  decimal_places=2,
                                  verbose_name="Balance")
    initial_balance = models.DecimalField(null=False,
                                          blank=False,
                                          max_digits=10,
                                          decimal_places=2,
                                          verbose_name="Initial balance")
    user = models.ForeignKey('users.User',
                             null=False,
                             blank=False,
                             on_delete=models.CASCADE,
                             related_name='+')
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    allow_negative = models.BooleanField(default=False,
                                         null=False,
                                         blank=False,
                                         verbose_name="Allow negative")

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return f"{self.name} account"

    def get_absolute_url(self):
        return reverse('account_detail', kwargs={'pk': self.pk})


class SystemReservedQuerySet(models.QuerySet):
    def delete(self):
        reserved_objects = self.filter(is_system_reserved=True)

        if reserved_objects.exists():
            reserved_str = ", ".join(str(obj) for obj in reserved_objects)
            raise ValidationError(f"Cannot delete system defaults: {reserved_str}.")

        return super().delete()

    def system_reserved(self):
        return self.filter(is_system_reserved=True)

    def transfer(self):
        return self.system_reserved().filter(is_transfer=True)


class CategoryManager(models.Manager.from_queryset(SystemReservedQuerySet)):
    pass


class Category(TimeStampMixin, StyleMixin):
    class CategoryType(models.TextChoices):
        INCOME = "+", "Income"
        EXPENSE = "-", "Expense"

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Category name")
    category_type = models.CharField(null=False,
                                     blank=False,
                                     max_length=1,
                                     choices=CategoryType,
                                     default=CategoryType.EXPENSE,
                                     verbose_name="Category type")
    user = models.ForeignKey('users.User',
                             null=False,
                             blank=False,
                             on_delete=models.CASCADE)

    is_system_reserved = models.BooleanField(blank=False, null=False, default=False, verbose_name="System reserved")
    is_transfer = models.BooleanField(blank=False, null=False, default=False, verbose_name="Transfer")

    objects = CategoryManager()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        constraints = [
            CheckConstraint(
                condition=Q(is_transfer=False) | Q(is_system_reserved=True),
                name='transfer_requires_system_reserved',
            ),
            UniqueConstraint(
                fields=['user', 'category_type'],
                condition=Q(is_transfer=True),
                name='unique_transfer_per_user_and_type',
            ),
        ]

    def __str__(self):
        return f"{self.name} category"

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs):
        if self.is_system_reserved:
            raise ValidationError(f"Cannot delete system default: {self}.")
        return super().delete(*args, **kwargs)

    @property
    def is_income(self):
        return self.category_type == self.CategoryType.INCOME

    @property
    def is_expense(self):
        return self.category_type == self.CategoryType.EXPENSE


class Transaction(TimeStampMixin):
    account = models.ForeignKey(null=False,
                                blank=False,
                                to=Account,
                                on_delete=models.CASCADE,
                                verbose_name="Account")
    category = models.ForeignKey(null=False,
                                 blank=False,
                                 to=Category,
                                 on_delete=models.CASCADE,
                                 verbose_name="Category")
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    amount = models.DecimalField(null=False,
                                 blank=False,
                                 max_digits=10,
                                 decimal_places=2,
                                 verbose_name="Amount")
    account_amount = models.DecimalField(null=False,
                                         blank=False,
                                         max_digits=10,
                                         decimal_places=2,
                                         verbose_name="Amount in account's currency")
    exchange_rate = models.DecimalField(max_digits=6,
                                        decimal_places=3,
                                        null=True,
                                        blank=True,
                                        verbose_name="Exchange rate to account currency")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    performed_date = models.DateField(default=timezone.localdate, verbose_name="Date")
    user = models.ForeignKey('users.User',
                             null=False,
                             blank=False,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"Transaction of {self.account.name}"

    def get_absolute_url(self):
        return reverse('dashboard')

    def get_update_url(self):
        transfer = Transfer.objects.filter(Q(txn_from=self) | Q(txn_to=self))
        if transfer:
            return reverse('transfer_update', kwargs={'pk': transfer[0].pk})
        else:
            return reverse('transaction_update', kwargs={'pk': self.pk})


class Transfer(TimeStampMixin):
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+')
    txn_from = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='+')

    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+')
    txn_to = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='+')

    class Meta:
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"

    def __str__(self):
        return f"Transfer {self.from_account.name} -> {self.to_account.name}"
