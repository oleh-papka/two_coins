from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView, UpdateView, CreateView

from budget.forms.account import AccountForm
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
        ctx["model_name"] = 'Account'
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
