from decimal import Decimal

from django import forms
from django.db.transaction import commit

from budget.models import Account, Transaction, Transfer
from budget.services.transfer import TransferService
from core.mixins.forms import BootstrapFormMixin
from core.services.decimal import format_decimal_for_input


class TransferForm(BootstrapFormMixin, forms.ModelForm):
    account_from = forms.ModelChoiceField(queryset=Account.objects.all(),
                                          required=True,
                                          empty_label="Account from")
    account_to = forms.ModelChoiceField(queryset=Account.objects.all(),
                                        required=True,
                                        empty_label="Account to")
    amount_from = forms.DecimalField(required=True,
                                     decimal_places=2,
                                     max_digits=10,
                                     min_value=Decimal("0.01"),
                                     label="Amount transferring")
    amount_to = forms.DecimalField(required=False,
                                   decimal_places=2,
                                   max_digits=10,
                                   min_value=Decimal("0.01"),
                                   label="Amount received")
    performed_date = forms.DateField(required=False, label="Date transferred",
                                     widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Transfer
        fields = ["account_from", "account_to", "amount_from", "amount_to", "performed_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()

        if self.instance and self.instance.pk:
            self.fields['account_from'].initial = self.instance.from_account
            self.fields['amount_from'].initial = format_decimal_for_input(abs(self.instance.txn_from.account_amount))
            self.fields['account_to'].initial = self.instance.to_account
            self.fields['amount_to'].initial = format_decimal_for_input(abs(self.instance.txn_to.account_amount))
            self.fields['performed_date'].initial = self.instance.txn_from.performed_date

    def clean(self):
        cleaned_data = super().clean()

        account_from = cleaned_data.get("account_from")
        account_to = cleaned_data.get("account_to")
        amount_from = cleaned_data.get("amount_from")
        amount_to = cleaned_data.get("amount_to")

        if account_from == account_to:
            self.add_error("account_to", "Cannot transfer to the same account")
            return cleaned_data
        if amount_from <= 0:
            self.add_error("amount_from", "Transfer amount must be positive")
            return cleaned_data

        if account_from.currency != account_to.currency:
            if amount_to in [Decimal("0"), None]:
                self.add_error("amount_to", "Required for transfer to account with different currency")
                return cleaned_data
            cleaned_data['amount_to'] = abs(amount_to)
        else:
            cleaned_data['amount_to'] = abs(amount_from)

        cleaned_data['amount_from'] = -abs(amount_from)

        return cleaned_data

    def save(self, *args, **kwargs):
        account_from = self.cleaned_data.get("account_from")
        account_to = self.cleaned_data.get("account_to")
        amount_from = self.cleaned_data.get("amount_from")
        amount_to = self.cleaned_data.get("amount_to")
        performed_date = self.cleaned_data.get("performed_date")

        if commit:
            return TransferService.create(account_from=account_from,
                                          account_to=account_to,
                                          amount_from=amount_from,
                                          amount_to=amount_to,
                                          performed_date=performed_date)
        return self.instance
