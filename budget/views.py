from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, DetailView

from budget.filters import TransactionFilter
from budget.forms.account import AccountForm
from budget.forms.category import CategoryForm
from budget.forms.transaction import TransactionForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.list import ListMixin
from budget.mixins.update import UpdateMixin
from budget.models import Account, Category, Transaction, Currency
from budget.services.account import AccountService
from budget.services.category import CategoryService
from budget.services.styling import StylingService
from budget.services.transaction import TransactionService


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'index.html'


class AccountListView(ListMixin):
    model = Account
    template_name = 'accounts_list.html'


class AccountUpdateView(UpdateMixin):
    model = Account
    form_class = AccountForm


class AccountCreateView(CreateMixin):
    model = Account
    form_class = AccountForm


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
                'id': transaction.id,
                'category': transaction.category.name,
                'badge_color': StylingService.get_badge_bootstrap_color(transaction.category.color),
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


class AccountDeleteView(DeleteMixin):
    model = Account
    success_url = reverse_lazy('account_list')
    model_service = AccountService

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = f'account {self.object.name} (this will delete all related transactions of that account)'
        return ctx


class CategoryListView(ListMixin):
    model = Category
    template_name = 'categories_list.html'


class CategoryUpdateView(UpdateMixin):
    model = Category
    form_class = CategoryForm


class CategoryCreateView(CreateMixin):
    model = Category
    form_class = CategoryForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        category_type = self.request.GET.get("category_type")
        if category_type:
            form.fields["category_type"].initial = category_type
        return form


class CategoryDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Category
    template_name = 'category_details.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        txns = []
        transactions = (
            Transaction.objects.filter(category=self.object, performed_date__month=timezone.now().month).order_by(
                '-performed_date')
        )

        for transaction in transactions:
            txns.append({
                'id': transaction.id,
                'account': transaction.account.name,
                'badge_color': StylingService.get_badge_bootstrap_color(transaction.account.color),
                'date': transaction.performed_date.strftime('%d.%m.%Y'),
                'amount': transaction.amount,
                'currency': transaction.currency.symbol,
            })

        ctx['transactions'] = txns

        ctx['stats_total'] = transactions.aggregate(total=Coalesce(Sum("amount"), Decimal("0")))['total']

        return ctx


class CategoryDeleteView(DeleteMixin):
    model = Category
    success_url = reverse_lazy('category_list')
    model_service = CategoryService

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = f'category {self.object.name} (this will delete all related transactions of that category)'
        return ctx


class TransactionCreateView(CreateMixin):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["account_currency_map"] = {
            str(account.id): str(account.currency_id)
            for account in Account.objects.select_related("currency")
        }

        ctx["currency_symbol_map"] = {
            str(currency.id): currency.symbol
            for currency in Currency.objects.all()
        }

        return ctx

    def form_valid(self, form):
        self.object = TransactionService.create_transaction(form)
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

        return ctx

    def form_valid(self, form):
        self.object = TransactionService.update_transaction(form)
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


class TransactionListView(ListMixin):
    model = Transaction
    template_name = 'transaction_list.html'
    filterset_class = TransactionFilter

    def get_queryset(self):
        return Transaction.objects.all().order_by('-performed_date')


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
