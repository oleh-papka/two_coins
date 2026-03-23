from django import forms

from .widgets import AmountCurrencyWidget


class AmountCurrencyField(forms.MultiValueField):
    def __init__(self, *, currency_queryset, **kwargs):
        currency_choices = [(obj.pk, f"{obj.symbol} ({obj.abbr})") for obj in currency_queryset]

        fields = (
            forms.DecimalField(required=True),
            forms.ModelChoiceField(queryset=currency_queryset, required=True),
        )

        widget = AmountCurrencyWidget(currency_choices=currency_choices)

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
