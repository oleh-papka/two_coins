from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView

from two_coins.settings import LOGIN_URL


class DeleteMixin(LoginRequiredMixin, DeleteView):
    login_url = LOGIN_URL
    template_name = 'delete.html'
    model_service = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Delete {self.object}'
        return ctx

    def get_service(self):
        if not self.model_service:
            raise ImproperlyConfigured("'model_service' is not set!")

        return self.model_service

    def form_valid(self, form):
        service = self.get_service()
        service.delete(self.object)

        return HttpResponseRedirect(self.get_success_url())
