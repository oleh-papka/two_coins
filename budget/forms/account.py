from django import forms

from budget.models import Account
from core.mixins.forms import BootstrapFormMixin
from core.services.decimal import format_decimal_for_input


class AccountForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Account
        fields = ('name', 'balance', 'currency', 'description', 'icon', 'color')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()

        if self.instance and self.instance.pk:
            self.initial["balance"] = format_decimal_for_input(self.instance.balance)
