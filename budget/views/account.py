from calendar import month
from collections import defaultdict
from decimal import Decimal

from debug_toolbar.panels import history
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.urls import reverse_lazy

from budget.forms.account import AccountForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.list import ListMixin
from budget.mixins.update import UpdateMixin
from budget.models import Account, Transaction
from budget.services.account import AccountService
from core.services.date import DateService


class AccountListView(ListMixin):
    model = Account
    template_name = 'accounts_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        from_default, to_default = DateService.get_date_start_end()

        from_date = DateService.parse_date(self.request.GET.get("from_date")) or from_default
        to_date = DateService.parse_date(self.request.GET.get("to_date")) or to_default

        account_id = self.request.GET.get("account_id") or self.object_list.first().id

        account_selected = Account.objects.get(id=account_id)
        base_txns = Transaction.objects.filter(
            performed_date__range=(from_date, to_date),
            account=account_selected,
        ).order_by('performed_date')

        ctx['totals_chart_labels'] = list()
        ctx['totals_chart_data'] = list()

        totals_incomes = 0
        totals_expenses = 0

        for txn in base_txns:
            if txn.account_amount > 0:
                totals_incomes += float(txn.account_amount)
            else:
                totals_expenses += float(txn.account_amount)

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

        history_txns = (
            Transaction.objects
            .filter(account=account_selected)
            .annotate(month=TruncMonth('performed_date'))
            .values('month')
            .annotate(total=Sum('account_amount'))
            .order_by('month')
        )

        ctx['totals_chart_labels'] = list()
        ctx['totals_chart_data'] = list()

        grand_total = 0
        for txn in history_txns:
            month = txn['month']
            grand_total += txn['total']
            if month.month == account_selected.created_at.month:
                grand_total += account_selected.initial_balance
            ctx['totals_chart_labels'].append(month.strftime('%b'))
            ctx['totals_chart_data'].append(float(grand_total))

        ctx['totals_chart_account'] = account_selected
        ctx['totals_chart_incomes'] = totals_incomes
        ctx['totals_chart_expenses'] = totals_expenses
        ctx['totals_chart_total'] = totals_expenses + totals_incomes
        ctx['total_by_currency'] = totals
        ctx["account_id"] = account_selected.id
        ctx["from_date_value"] = from_date.strftime("%Y-%m-%d")
        ctx["to_date_value"] = to_date.strftime("%Y-%m-%d")
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

    def form_valid(self, form):
        if 'balance' in form.changed_data:
            AccountService.modify_account_balance(form.instance.pk, form.cleaned_data.get('balance', Decimal('0')))

        return super().form_valid(form)


class AccountDeleteView(DeleteMixin):
    model = Account
    success_url = reverse_lazy('account_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = f'account {self.object.name} (this will delete all related transactions of that account)'
        return ctx
