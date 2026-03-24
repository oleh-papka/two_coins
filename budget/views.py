from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, UpdateView, CreateView, DetailView, DeleteView

from budget.filters import TransactionFilter
from budget.forms.account import AccountForm
from budget.forms.category import CategoryForm
from budget.forms.transaction import TransactionForm
from budget.mixins.list import ListMixin
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


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Account
    form_class = AccountForm
    template_name = 'change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Update {self.object}'
        return ctx


class AccountCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Account
    form_class = AccountForm
    template_name = 'change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Create {self.object}'
        ctx['model_name'] = 'Account'
        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


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


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Account
    template_name = 'delete.html'
    success_url = reverse_lazy('account_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Delete {self.object}'
        ctx['object_repr'] = f'account {self.object.name} (this will delete all related transactions of that account)'
        return ctx

    def form_valid(self, form):
        AccountService.delete_account(self.object)

        return HttpResponseRedirect(self.get_success_url())


class CategoryListView(ListMixin):
    model = Category
    template_name = 'categories_list.html'


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Category
    form_class = CategoryForm
    template_name = 'change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Update {self.object}'
        return ctx


class CategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Category
    form_class = CategoryForm
    template_name = 'change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Create {self.object}'
        ctx['model_name'] = 'Category'
        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

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


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Category
    template_name = 'delete.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Delete {self.object}'
        ctx['object_repr'] = f'category {self.object.name} (this will delete all related transactions of that category)'
        return ctx

    def form_valid(self, form):
        CategoryService.delete_category(self.object)

        return HttpResponseRedirect(self.get_success_url())


class TransactionCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Create {self.object}'
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


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Update {self.object}'
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


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Transaction
    template_name = 'delete.html'
    success_url = reverse_lazy('transaction_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Delete {self.object}'
        ctx['object_repr'] = (
            f'transaction of {self.object.account_amount}{self.object.currency.symbol} from {self.object.account.name}'
        )
        return ctx

    def form_valid(self, form):
        TransactionService.delete_transaction(self.object)

        return HttpResponseRedirect(self.get_success_url())
