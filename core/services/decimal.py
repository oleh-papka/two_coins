from decimal import Decimal


def format_decimal_for_input(value):
    if value is None:
        return ""
    value = Decimal(value)
    return format(value.quantize(Decimal("1")) if value == value.to_integral() else value.normalize(), "f")

