from decimal import Decimal

from django.db import transaction
from django.db.models import F

from budget.forms.transaction import TransactionForm
from budget.models import Transaction, Account


class TransactionService:

    @staticmethod
    def _change_account_balance(account_id: int, delta: Decimal) -> None:
        Account.objects.filter(pk=account_id).update(
            balance=F("balance") + delta
        )

    @staticmethod
    @transaction.atomic
    def add_from_object(txn: Transaction) -> Transaction:
        txn.save()
        TransactionService._change_account_balance(txn.account_id, txn.account_amount)
        return txn

    @staticmethod
    @transaction.atomic
    def create(form: TransactionForm) -> Transaction:
        txn: Transaction = form.save(commit=False)
        return TransactionService.add_from_object(txn)

    @staticmethod
    @transaction.atomic
    def update(form: TransactionForm):
        if not form.instance.pk:
            raise ValueError("Transaction must exist for update")

        old_txn = Transaction.objects.select_for_update().get(pk=form.instance.pk)
        txn: Transaction = form.save()

        if old_txn.account_id == txn.account_id:
            delta = txn.account_amount - old_txn.account_amount
            TransactionService._change_account_balance(txn.account_id, delta)
        else:
            TransactionService._change_account_balance(old_txn.account_id, -old_txn.account_amount)
            TransactionService._change_account_balance(txn.account_id, txn.account_amount)

        return txn

    @staticmethod
    @transaction.atomic
    def delete(txn: Transaction):
        if not txn.pk:
            raise ValueError("Transaction must exist for delete")

        txn = Transaction.objects.select_for_update().get(pk=txn.pk)
        TransactionService._change_account_balance(txn.account_id, -txn.account_amount)
        txn.delete()
