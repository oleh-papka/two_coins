from django import forms

from budget.models import Transaction
from core.mixins.forms import BootstrapFormMixin


class TransactionForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Transaction
        fields = ('account', 'category', 'amount', 'currency', 'amount_converted', 'description', 'performed_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()
