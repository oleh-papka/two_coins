from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from budget.models import Account, Category


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'index.html'


class AccountListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Account
    template_name = 'accounts_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = 'Accounts'
        return ctx


class CategoryListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Category
    template_name = 'categories_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = 'Categories'
        return ctx
