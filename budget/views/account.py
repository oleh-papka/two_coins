import json
from collections import defaultdict
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView

from budget.forms.account import AccountForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.list import ListMixin
from budget.mixins.update import UpdateMixin
from budget.models import Account, Transaction


class AccountDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Account
    template_name = 'account_details.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        transactions = (
            Transaction.objects.filter(account=self.object,
                                       performed_date__month=timezone.now().month).order_by('-performed_date')
        )

        ctx['transactions'] = transactions

        stats = transactions.aggregate(
            income=Coalesce(Sum("amount", filter=Q(amount__gt=0)), Decimal("0")),
            expenses=Coalesce(Sum("amount", filter=Q(amount__lt=0)), Decimal("0")),
            total=Coalesce(Sum("amount"), Decimal("0")),
        )
        ctx['stats'] = stats

        return ctx


class AccountListView(ListMixin):
    model = Account
    template_name = 'accounts_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        totals = list(
            self.object_list.values(
                currency_symbol=F('currency__symbol'),
                currency_name=F('currency__name'),
                currency_abbr=F('currency__abbr')
            ).annotate(total_balance=Sum('balance'))
        )

        grouped_by_currency = defaultdict(list)
        for account in self.object_list:
            grouped_by_currency[account.currency.abbr].append(account)

        chart_data_map = {}
        for abbr, accounts in grouped_by_currency.items():
            if len(accounts) <= 1:
                chart_data_map[abbr] = []
                continue

            chart_data_map[abbr] = [
                {
                    'value': float(account.balance or 0),
                    'name': account.name,
                }
                for account in accounts
            ]

        for item in totals:
            item['total_balance'] = float(item['total_balance'])
            item['chart_data'] = chart_data_map.get(item['currency_abbr'], [])

        ctx['total_by_currency'] = totals
        return ctx


class AccountCreateView(CreateMixin):
    model = Account
    form_class = AccountForm

    def form_valid(self, form):
        form.instance.initial_balance = form.instance.balance
        return super().form_valid(form)


class AccountUpdateView(UpdateMixin):
    model = Account
    form_class = AccountForm


class AccountDeleteView(DeleteMixin):
    model = Account
    success_url = reverse_lazy('account_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = f'account {self.object.name} (this will delete all related transactions of that account)'
        return ctx
