from decimal import Decimal

from django import forms

from .widgets import AmountCurrencyWidget
from ..models import Currency


class AmountCurrencyField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = (
            forms.DecimalField(required=True, decimal_places=2, max_digits=10),
            forms.ModelChoiceField(queryset=Currency.objects.none(), required=True),
        )

        widget = AmountCurrencyWidget()

        super().__init__(
            fields=fields,
            widget=widget,
            require_all_fields=True,
            **kwargs,
        )

    def compress(self, data_list):
        if not data_list:
            return {"amount": None, "currency": None}

        return {
            "amount": data_list[0],
            "currency": data_list[1],
        }
