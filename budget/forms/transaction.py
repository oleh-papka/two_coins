from django import forms

from budget.forms.fields import AmountCurrencyField
from budget.models import Transaction, Currency, Category
from core.mixins.forms import BootstrapFormMixin
from core.services.decimal import format_decimal_for_input


class TransactionForm(BootstrapFormMixin, forms.ModelForm):
    amount_currency = AmountCurrencyField(label="Amount")
    account_amount = forms.DecimalField(required=False,
                                        decimal_places=2,
                                        max_digits=10,
                                        label="Amount in account's currency")

    class Meta:
        model = Transaction
        fields = ('account', 'category', 'amount_currency', 'account_amount', 'description', 'performed_date')
        widgets = {'performed_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()

        self.fields["category"].queryset = Category.objects.user_accessible().order_by("is_system_reserved")

        currencies = Currency.objects.all()
        self.fields["amount_currency"].fields[1].queryset = currencies
        currency_choices = [(obj.pk, f"{obj.symbol} ({obj.abbr})") for obj in currencies]
        self.fields['amount_currency'].widget.widgets[1].choices = currency_choices

        if self.instance and self.instance.pk:
            self.initial["amount_currency"] = {
                "amount": format_decimal_for_input(abs(self.instance.amount)),
                "currency": self.instance.currency_id,
            }
            self.initial["account_amount"] = format_decimal_for_input(abs(self.instance.account_amount))

    def clean(self):
        cleaned_data = super().clean()

        amount_currency = cleaned_data.get("amount_currency")
        category = cleaned_data.get("category")
        account = cleaned_data.get("account")
        account_amount = cleaned_data.get("account_amount")

        if not all([amount_currency, category, account]):
            return cleaned_data

        amount = amount_currency.get("amount")
        currency = amount_currency.get("currency")

        if amount is None:
            return cleaned_data

        normalized_amount = abs(amount) if category.is_income else -abs(amount)

        cleaned_data["amount_currency"] = {
            **amount_currency,
            "amount": normalized_amount,
        }

        if currency == account.currency:
            account_amount = normalized_amount
        else:
            if account_amount is None:
                self.add_error("account_amount", "Required for currency conversion")
                return cleaned_data
            else:
                account_amount = (
                    abs(account_amount) if category.is_income else -abs(account_amount)
                )

        cleaned_data["account_amount"] = account_amount

        if category.is_income:
            return cleaned_data

        if not account.allow_negative:
            if self.instance and self.instance.pk:
                delta = account_amount - self.instance.account_amount
            else:
                delta = account_amount

            if account.balance + delta < 0:
                self.add_error("amount_currency",
                               "Account does not have enough balance (change amount or allow negative balance for an account)")
                self.add_error("account_amount",
                               "Account does not have enough balance (change amount or allow negative balance for an account)")
                return cleaned_data

        return cleaned_data

    def full_clean(self):
        super().full_clean()

        self.fields["amount_currency"].widget.attrs["is_invalid"] = True if "amount_currency" in self.errors else False

    def save(self, commit=True):
        instance = super().save(commit=False)

        amount_currency = self.cleaned_data["amount_currency"]
        instance.amount = amount_currency["amount"]
        instance.currency = amount_currency["currency"]

        if commit:
            instance.save()

        return instance
