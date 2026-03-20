from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from budget.models import Account


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'index.html'


class AccountListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Account
    template_name = ''

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
