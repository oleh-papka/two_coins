from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from two_coins.settings import LOGIN_URL


class UpdateMixin(LoginRequiredMixin, UpdateView):
    login_url = LOGIN_URL
    template_name = 'change_form.html'

    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Update {self.object}'
        return ctx
