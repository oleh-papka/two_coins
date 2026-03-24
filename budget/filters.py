import django_filters
from django import forms

from budget.models import Transaction
from core.mixins.forms import BootstrapFormMixin
from core.services.date import DateService


class TransactionFilter(BootstrapFormMixin, django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='performed_date', lookup_expr='gte',
                                          widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = django_filters.DateFilter(field_name='performed_date', lookup_expr='lte',
                                        widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Transaction
        fields = ['account', 'category', 'date_from', 'date_to']

    def get_form_fields(self):
        return self.form.fields

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        self._init_bootstrap()

        if not data:
            first_day, last_day = DateService.get_date_start_end()

            self.filters['date_from'].extra['initial'] = first_day
            self.filters['date_to'].extra['initial'] = last_day

            self.form.initial['date_from'] = first_day
            self.form.initial['date_to'] = last_day

        for name, field in self.form.fields.items():
            field.widget.attrs['style'] = 'width: auto; max-width: 250px;'
            if hasattr(field, "empty_label"):
                field.empty_label = field.label
