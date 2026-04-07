from decimal import Decimal

from django.db import transaction

from budget.models import Account, Currency, Category, Transaction


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



    @staticmethod
    @transaction.atomic
    def modify_account_balance(account_id: int, new_balance: Decimal) -> None:
        account = Account.objects.select_for_update().get(pk=account_id)
        user = account.user

        delta = new_balance - account.balance
        if delta == 0:
            return

        category_type = '+' if delta > 0 else '-'
        category = Category.objects.get(
            user=user,
            is_system_reserved=True,
            category_type=category_type,
            is_transfer=False
        )

        Transaction.objects.create(
            account=account,
            category=category,
            currency=account.currency,
            amount=delta,
            account_amount=delta,
            exchange_rate=Decimal("1"),
            description="Balance correction",
            user=user,
        )
