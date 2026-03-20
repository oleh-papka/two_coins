from django import forms

from budget.models import Account
from core.mixins.forms import BootstrapFormMixin


class AccountForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Account
        fields = ('name', 'balance', 'currency', 'description', 'icon')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()
