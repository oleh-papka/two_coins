from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction as db_transaction
from django.db.models import F
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
                                  default=Decimal("0"),
                                  max_digits=10,
                                  decimal_places=2,
                                  verbose_name="Balance")
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

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return f"{self.name} account"

    def withdraw(self, amount: Decimal):
        amount = abs(amount)

        with db_transaction.atomic():
            account = Account.objects.select_for_update().get(pk=self.pk)

            if account.balance < amount:
                raise ValidationError("Insufficient funds")

            account.balance = F("balance") - amount
            account.save(update_fields=["balance"])
            account.refresh_from_db(fields=["balance"])
            self.balance = account.balance

    def deposit(self, amount: Decimal):
        amount = abs(amount)
        Account.objects.filter(pk=self.pk).update(balance=F("balance") + amount)
        self.refresh_from_db(fields=["balance"])

    def get_absolute_url(self):
        return reverse('account_detail', kwargs={'pk': self.pk})


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

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} category"

    def get_absolute_url(self):
        return reverse('category_list')


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
                                 default=Decimal("0"),
                                 max_digits=10,
                                 decimal_places=2,
                                 verbose_name="Amount")
    amount_converted = models.DecimalField(null=True,
                                           blank=True,
                                           default=None,
                                           max_digits=10,
                                           decimal_places=2,
                                           verbose_name="Amount in account's currency")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    performed_date = models.DateField(default=timezone.localdate, verbose_name="Date")

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"Transaction of {self.account.name}"

    def get_absolute_url(self):
        return reverse('dashboard')


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
