from datetime import datetime, date

from django.contrib import messages
from django.db.models import Sum, F, Case, When, CharField, Value
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from budget.forms.category import CategoryForm, ReservedCategoryUpdateForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.list import ListMixin
from budget.mixins.update import UpdateMixin
from budget.models import Category, Transaction, Currency
from core.services.date import DateService


class CategoryListView(ListMixin):
    model = Category
    template_name = 'categories_list.html'

    def get_queryset(self):
        return super().get_queryset().order_by('is_system_reserved')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        from_default, to_default = DateService.get_date_start_end()

        from_date = DateService.parse_date(self.request.GET.get("from_date")) or from_default
        to_date = DateService.parse_date(self.request.GET.get("to_date")) or to_default

        currency_id = self.request.GET.get("currency_id") or 1

        base_txns = Transaction.objects.filter(
            performed_date__range=(from_date, to_date),
            account__user=self.request.user,
        ).order_by('-performed_date')

        currency_ids = base_txns.values_list("account__currency_id", flat=True).distinct()
        currencies = list(
            Currency.objects.filter(id__in=currency_ids).only("id", "abbr", "name", "symbol")
        )

        curr = get_object_or_404(
            Currency.objects.only("id", "abbr", "name", "symbol"),
            id=currency_id,
        )

        txns = base_txns.filter(account__currency_id=curr.id)

        grouped = list(
            txns.annotate(
                type_name=Case(
                    When(account_amount__gt=0, then=Value("income")),
                    When(account_amount__lt=0, then=Value("expense")),
                    output_field=CharField(),
                ),
                category_name=F("category__name"),
            )
            .values("type_name", "category_name")
            .annotate(total_amount=Sum("account_amount"))
            .order_by("type_name", "category_name")
        )

        income_labels = []
        income_values = []
        expense_labels = []
        expense_values = []

        for row in grouped:
            amount = float(row["total_amount"])
            if row["type_name"] == "income":
                income_labels.append(row["category_name"])
                income_values.append(amount)
            else:
                expense_labels.append(row["category_name"])
                expense_values.append(amount)

        income_data = {
            "total_amount": sum(income_values),
            "currency_abbr": curr.abbr,
            "currency_name": curr.name,
            "currency_symbol": curr.symbol,
            "type_name": "income",
            "chart_data": {
                "labels": income_labels,
                "data": income_values,
            },
        }

        expense_data = {
            "total_amount": sum(expense_values),
            "currency_abbr": curr.abbr,
            "currency_name": curr.name,
            "currency_symbol": curr.symbol,
            "type_name": "expense",
            "chart_data": {
                "labels": expense_labels,
                "data": expense_values,
            },
        }

        ctx["totals"] = [expense_data, income_data]
        ctx["currencies"] = currencies
        ctx["currency_id"] = curr.id
        ctx["from_date_value"] = from_date.strftime("%Y-%m-%d")
        ctx["to_date_value"] = to_date.strftime("%Y-%m-%d")

        return ctx


class CategoryCreateView(CreateMixin):
    model = Category
    form_class = CategoryForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        category_type = self.request.GET.get("category_type")
        if category_type:
            form.fields["category_type"].initial = category_type
        return form


class CategoryUpdateView(UpdateMixin):
    model = Category
    form_class = CategoryForm

    def get_form_class(self):
        if self.object.is_system_reserved:
            messages.info(self.request, "This is system reserved object, you can only change it's style.")
            return ReservedCategoryUpdateForm
        return CategoryForm


class CategoryDeleteView(DeleteMixin):
    model = Category
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = f'category {self.object.name} (this will delete all related transactions of that category)'
        return ctx

    def get(self, request, *args, **kwargs):
        self.object: Category = self.get_object()
        if self.object.is_system_reserved:
            messages.info(self.request, "This is system reserved object, you can only change it's style.")
            return HttpResponseRedirect(self.object.get_absolute_url())

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if self.object.is_system_reserved:
            messages.info(self.request, "This is system reserved object, you can only change it's style.")
            return HttpResponseRedirect(self.object.get_absolute_url())

        return super().form_valid(form)
