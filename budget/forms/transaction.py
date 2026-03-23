from django import forms
from django.forms import widgets

from budget.forms.fields import AmountCurrencyField
from budget.models import Transaction, Currency
from core.mixins.forms import BootstrapFormMixin


class TransactionForm(BootstrapFormMixin, forms.ModelForm):
    amount_currency = AmountCurrencyField(currency_queryset=Currency.objects.all(), label="Amount")

    class Meta:
        model = Transaction
        fields = ('account', 'category', 'amount_currency', 'account_amount', 'description', 'performed_date')
        widgets = {
            'performed_date': forms.DateInput(attrs={'type': 'date'},),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()

        if self.instance.pk:
            self.initial["amount_currency"] = {
                "amount": self.instance.amount,
                "currency": self.instance.currency_id,
            }

    def clean(self):
        cleaned_data = super().clean()

        amount_currency = cleaned_data.get("amount_currency")
        category = cleaned_data.get("category")

        if not amount_currency or not category:
            return cleaned_data

        amount = amount_currency.get("amount")
        if amount is None:
            return cleaned_data

        amount_currency["amount"] = abs(amount) if category.is_income else -abs(amount)

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
