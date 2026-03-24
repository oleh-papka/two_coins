from django import forms

from budget.forms.widgets import add_css_class


class BootstrapFormMixin:
    def _get_widget_class(self, field):
        widget = field.widget

        if isinstance(widget, forms.CheckboxInput):
            return "form-check-input"

        if isinstance(widget, forms.Select):
            return "form-select"

        if isinstance(widget, (forms.TextInput, forms.NumberInput, forms.EmailInput,
                               forms.URLInput, forms.PasswordInput, forms.Textarea,
                               forms.DateInput, forms.DateTimeInput, forms.TimeInput,
                               forms.FileInput)):
            return "form-control"

        return ""

    def _supports_placeholder(self, field):
        return isinstance(
            field.widget,
            (
                forms.TextInput,
                forms.NumberInput,
                forms.EmailInput,
                forms.URLInput,
                forms.PasswordInput,
                forms.Textarea,
            ),
        )

    def get_form_fields(self):
        return self.fields

    def _init_bootstrap(self):
        for name, field in self.get_form_fields().items():
            widget = field.widget

            if isinstance(widget, forms.MultiWidget):
                continue

            widget_class = self._get_widget_class(field)
            if widget_class:
                widget.attrs["class"] = add_css_class(
                    widget.attrs.get("class"),
                    widget_class,
                )

            if self._supports_placeholder(field) and field.label:
                widget.attrs.setdefault("placeholder", field.label)

    def full_clean(self):
        super().full_clean()

        for name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.MultiWidget):
                continue

            if name in self.errors:
                widget.attrs["class"] = add_css_class(
                    widget.attrs.get("class"),
                    "is-invalid",
                )
