from collections import defaultdict

from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django_filters.views import FilterView

from budget.filters import TransactionFilter
from budget.forms.transaction import TransactionForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.list import ListMixin
from budget.mixins.update import UpdateMixin
from budget.models import Account, Category, Transaction, Currency
from budget.services.transaction import TransactionService


class TransactionListView(FilterView, ListMixin):
    model = Transaction
    template_name = 'transaction_list.html'
    filterset_class = TransactionFilter

    def get_queryset(self):
        return super().get_queryset().order_by('-performed_date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        currencies = set(
            self.object_list
            .values_list('account__currency__id', flat=True).distinct()
        )

        charts_by_currency = []

        for currency_id in currencies:
            currency = Currency.objects.get(id=currency_id)
            txns = (
                self.object_list
                .filter(account__currency=currency)
                .select_related('category', 'account')
                .order_by('performed_date')
            )

            transactions_by_date = defaultdict(dict)
            categories_set = set()

            for txn in txns:
                date_key = txn.performed_date.strftime('%Y-%m-%d')
                category_name = txn.category.name
                categories_set.add(category_name)

                # if multiple txns of same category exist on same day, sum them
                transactions_by_date[date_key][category_name] = (
                        transactions_by_date[date_key].get(category_name, 0) + float(txn.account_amount)
                )

            dates = sorted(transactions_by_date.keys())
            categories = sorted(categories_set)

            series = []
            for category in categories:
                series.append({
                    "name": category,
                    "type": "bar",
                    "stack": "transactions",
                    "data": [
                        transactions_by_date[date].get(category, '-')
                        for date in dates
                    ],
                })

            charts_by_currency.append({
                "currency_name": currency.name,
                "currency_symbol": currency.symbol,
                "dates": dates,
                "categories": categories,
                "series": series,
            })

        ctx["charts_by_currency"] = charts_by_currency
        return ctx


class TransactionCreateView(CreateMixin):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        accounts = Account.objects.filter(user=self.request.user).select_related("currency")
        ctx["account_currency_map"] = {str(account.id): str(account.currency_id) for account in accounts}

        ctx["currency_symbol_map"] = {
            str(currency.id): currency.symbol
            for currency in Currency.objects.all()
        }

        ctx["category_symbol_map"] = {
            str(category.id): '-' if category.is_expense else '+' for category in Category.objects.all()
        }

        if len(accounts) == 1:
            self.initial["account"] = accounts[0]

        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = TransactionService.create(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        category = self.request.GET.get("category")
        account = self.request.GET.get("account")

        if category:
            form.fields["category"].initial = Category.objects.get(id=category)

        if account:
            form.fields["account"].initial = Account.objects.get(id=account)

        return form


class TransactionUpdateView(UpdateMixin):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['model_name'] = 'Transaction'

        ctx["account_currency_map"] = {
            str(account.id): str(account.currency_id)
            for account in Account.objects.select_related("currency")
        }

        ctx["currency_symbol_map"] = {
            str(currency.id): currency.symbol
            for currency in Currency.objects.all()
        }

        ctx["category_symbol_map"] = {
            str(category.id): '-' if category.is_expense else '+' for category in Category.objects.all()
        }

        return ctx

    def form_valid(self, form):
        self.object = TransactionService.update(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        category = self.request.GET.get("category")
        account = self.request.GET.get("account")

        if category:
            form.fields["category"].initial = Category.objects.get(id=category)

        if account:
            form.fields["account"].initial = Account.objects.get(id=account)

        return form


class TransactionDeleteView(DeleteMixin):
    model = Transaction
    success_url = reverse_lazy('transaction_list')
    model_service = TransactionService

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = (
            f'transaction of {self.object.account_amount}{self.object.currency.symbol} from {self.object.account.name}'
        )
        return ctx
