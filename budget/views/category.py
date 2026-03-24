from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView

from budget.forms.category import CategoryForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.list import ListMixin
from budget.mixins.update import UpdateMixin
from budget.models import Category, Transaction
from budget.services.category import CategoryService
from budget.services.styling import StylingService


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


class CategoryListView(ListMixin):
    model = Category
    template_name = 'categories_list.html'


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


class CategoryDeleteView(DeleteMixin):
    model = Category
    success_url = reverse_lazy('category_list')
    model_service = CategoryService

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = f'category {self.object.name} (this will delete all related transactions of that category)'
        return ctx
