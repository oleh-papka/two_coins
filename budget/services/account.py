from django.db import transaction

from budget.models import Account, Currency


class AccountService:
    DEFAULT_CURRENCY = 'USD'
    DEFAULT_ACCOUNT_DATA = {
        'name': 'Default',
        'balance': 0,
        'initial_balance': 0,
        'color': 'bg-body',
        'icon': '💳',
    }

    @staticmethod
    @transaction.atomic
    def create_default(user) -> Account:
        currency = Currency.objects.get(abbr=AccountService.DEFAULT_CURRENCY)

        return Account.objects.create(user=user,
                                      currency=currency,
                                      **AccountService.DEFAULT_ACCOUNT_DATA)
