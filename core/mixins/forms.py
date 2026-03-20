from django import forms


class BootstrapFormMixin:
    def _get_widget_class(self, field):
        if isinstance(field.widget, forms.CheckboxInput):
            return "form-check-input"
        if isinstance(field.widget, forms.Select):
            return "form-select"
        return "form-control"

    def _init_bootstrap(self):
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            widget_class = self._get_widget_class(field)

            error_class = " is-invalid" if name in self.errors else ""
            field.widget.attrs["class"] = f"{existing} {widget_class}{error_class}".strip()
            field.widget.attrs.setdefault("placeholder", field.label)
