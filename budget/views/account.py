from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
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

        txns = []
        transactions = (
            Transaction.objects.filter(account=self.object,
                                       performed_date__month=timezone.now().month).order_by('-performed_date')
        )

        for transaction in transactions:
            txns.append({
                'url': transaction.get_update_url(),
                'category': transaction.category.name,
                'badge_color': transaction.category.color,
                'date': transaction.performed_date.strftime('%d.%m.%Y'),
                'amount': transaction.amount,
                'currency': transaction.currency.symbol
            })

        ctx['transactions'] = txns

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


class AccountCreateView(CreateMixin):
    model = Account
    form_class = AccountForm


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
