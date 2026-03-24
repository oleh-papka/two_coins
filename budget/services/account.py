from django.db import transaction

from budget.models import Account
from budget.services.transaction import TransactionService


class AccountService:

    @staticmethod
    @transaction.atomic
    def delete_account(account: Account):
        txns = account.transaction_set.all()

        for txn in txns:
            TransactionService.delete_transaction(txn)

        account.delete()
