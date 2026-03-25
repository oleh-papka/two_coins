from decimal import Decimal

from django import forms


def add_css_class(existing: str | None, new_class: str) -> str:
    classes = (existing or "").split()
    for cls in new_class.split():
        if cls not in classes:
            classes.append(cls)
    return " ".join(classes).strip()


class AmountCurrencyWidget(forms.MultiWidget):
    template_name = "widgets/amount_currency.html"

    def __init__(self, currency_choices=(), attrs=None):
        widgets = [
            forms.NumberInput(attrs={
                "step": "0.01",
                "value": Decimal("0"),
                "placeholder": "Amount",
            }),
            forms.Select(
                choices=currency_choices,
                attrs={
                    "style": "max-width: 120px",
                },
            ),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """
        Supports:
        - {"amount": ..., "currency": ...}
        - None
        """
        if isinstance(value, dict):
            currency = value.get("currency")
            if hasattr(currency, "pk"):
                currency = currency.pk
            return [value.get("amount"), currency]
        return [None, None]

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        subwidgets = context["widget"]["subwidgets"]

        is_invalid = bool(context["widget"]["attrs"].get("is_invalid"))

        subwidgets[0]["attrs"]["class"] = add_css_class(
            subwidgets[0]["attrs"].get("class"),
            "form-control",
        )
        subwidgets[1]["attrs"]["class"] = add_css_class(
            subwidgets[1]["attrs"].get("class"),
            "form-select",
        )

        if is_invalid:
            subwidgets[0]["attrs"]["class"] = add_css_class(
                subwidgets[0]["attrs"]["class"],
                "is-invalid",
            )
            subwidgets[1]["attrs"]["class"] = add_css_class(
                subwidgets[1]["attrs"]["class"],
                "is-invalid",
            )

        context["widget"]["error_messages"] = context["widget"]["attrs"].get("error_messages", [])
        return context
