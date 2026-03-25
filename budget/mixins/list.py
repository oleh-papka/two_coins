from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from two_coins.settings import LOGIN_URL


class ListMixin(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = self.model._meta.verbose_name_plural
        return ctx

    class Meta:
        abstract = True
