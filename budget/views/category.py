from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView

from budget.forms.category import CategoryForm, ReservedCategoryUpdateForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.list import ListMixin
from budget.mixins.update import UpdateMixin
from budget.models import Category, Transaction


class CategoryDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Category
    template_name = 'category_details.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        transactions = (
            Transaction.objects.filter(category=self.object, performed_date__month=timezone.now().month).order_by(
                '-performed_date')
        )

        ctx['transactions'] = transactions
        ctx['stats_total'] = transactions.aggregate(total=Coalesce(Sum("amount"), Decimal("0")))['total']

        return ctx


class CategoryListView(ListMixin):
    model = Category
    template_name = 'categories_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).order_by('is_system_reserved')


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
