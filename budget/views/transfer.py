from budget.forms.transfer import TransferForm
from budget.mixins.create import CreateMixin
from budget.mixins.delete import DeleteMixin
from budget.mixins.update import UpdateMixin
from budget.models import Transfer, Account
from budget.services.transfer import TransferService


class TransferAddView(CreateMixin):
    form_class = TransferForm
    model = Transfer
    template_name = 'transfer_form.html'

    def get_success_url(self):
        return self.object.from_account.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = f'Transfer funds'
        ctx['model_name'] = "Transfer"

        accounts = Account.objects.filter(user=self.request.user).select_related("currency")
        ctx["account_currency_map"] = {str(account.id): str(account.currency.symbol) for account in accounts}

        return ctx

    def get_initial(self):
        initial = super().get_initial()
        account_pk = self.request.GET.get("account_from")

        if account_pk:
            initial['account_from'] = Account.objects.get(id=account_pk)

        return initial


class TransferUpdateView(UpdateMixin):
    form_class = TransferForm
    model = Transfer
    template_name = 'transfer_form.html'

    def get_success_url(self):
        return self.object.from_account.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = "Transfer"

        return ctx

    def form_valid(self, form):
        old_obj = self.get_object()
        TransferService.delete(old_obj)
        return super().form_valid(form)


class TransferDeleteView(DeleteMixin):
    model = Transfer
    model_service = TransferService

    def get_success_url(self):
        return self.object.from_account.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_repr'] = str(self.object)
        return ctx
