from decimal import Decimal

from django import forms

from budget.forms.fields import AmountCurrencyField
from budget.models import Transaction, Currency
from core.mixins.forms import BootstrapFormMixin
from core.services.decimal import format_decimal_for_input


class TransactionForm(BootstrapFormMixin, forms.ModelForm):
    amount_currency = AmountCurrencyField(label="Amount")

    class Meta:
        model = Transaction
        fields = ('account', 'category', 'amount_currency', 'account_amount', 'description', 'performed_date')
        widgets = {'performed_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()

        currencies = Currency.objects.all()
        self.fields["amount_currency"].fields[1].queryset = currencies
        currency_choices = [(obj.pk, f"{obj.symbol} ({obj.abbr})") for obj in currencies]
        self.fields['amount_currency'].widget.widgets[1].choices = currency_choices

        if self.instance and self.instance.pk:
            self.initial["amount_currency"] = {
                "amount": format_decimal_for_input(self.instance.amount),
                "currency": self.instance.currency_id,
            }

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
            cleaned_data["account_amount"] = normalized_amount
        else:
            if account_amount is None:
                self.add_error("account_amount", "Required for currency conversion")
            else:
                cleaned_data["account_amount"] = (
                    abs(account_amount) if category.is_income else -abs(account_amount)
                )

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
