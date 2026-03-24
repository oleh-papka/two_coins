from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from two_coins.settings import LOGIN_URL


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = LOGIN_URL
    template_name = 'index.html'
