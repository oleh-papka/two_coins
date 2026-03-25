from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from two_coins.settings import LOGIN_URL


class CreateMixin(LoginRequiredMixin, CreateView):
    login_url = LOGIN_URL
    template_name = 'change_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        model_name = self.model.__name__
        ctx['title'] = f'Create {model_name}'
        ctx['model_name'] = model_name
        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    class Meta:
        abstract = True
