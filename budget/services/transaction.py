from django.db import transaction

from budget.forms.transaction import TransactionForm
from budget.models import Transaction


class TransactionService:

    @staticmethod
    @transaction.atomic
    def create_transaction(form: TransactionForm):
        txn: Transaction = form.save()

        account = txn.account
        account.balance += txn.account_amount

        account.save(update_fields=["balance"])

        return txn

    @staticmethod
    @transaction.atomic
    def update_transaction(form: TransactionForm):
        if not form.instance.pk:
            raise ValueError("Transaction must exist for update")

        old_txn = Transaction.objects.select_for_update().get(pk=form.instance.pk)

        txn: Transaction = form.save()

        if old_txn.account_id == txn.account_id:
            delta = txn.account_amount - old_txn.account_amount
            txn.account.balance += delta
            txn.account.save(update_fields=["balance"])
        else:
            old_txn.account.balance -= old_txn.account_amount
            old_txn.account.save(update_fields=["balance"])

            txn.account.balance += txn.account_amount
            txn.account.save(update_fields=["balance"])

        return txn

    @staticmethod
    @transaction.atomic
    def delete_transaction(txn: Transaction):
        txn = Transaction.objects.select_related("account").select_for_update().get(pk=txn.pk)

        account = txn.account

        account.balance -= txn.account_amount
        account.save(update_fields=["balance"])

        txn.delete()
