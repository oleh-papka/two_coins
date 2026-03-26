from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import F

from budget.forms.transaction import TransactionForm
from budget.models import Transaction, Account


class TransactionService:
    EXCHANGE_RATE_PRECISION = Decimal("0.001")

    @staticmethod
    def _change_account_balance(account_id: int, delta: Decimal) -> None:
        Account.objects.filter(pk=account_id).update(
            balance=F("balance") + delta
        )

    @staticmethod
    def _set_exchange_rate(txn: Transaction) -> None:
        if txn.amount == 0:
            raise ValueError("Transaction amount cannot be zero when calculating exchange rate")

        if txn.amount != txn.account_amount:
            txn.exchange_rate = (txn.account_amount / txn.amount).quantize(
                TransactionService.EXCHANGE_RATE_PRECISION,
                rounding=ROUND_HALF_UP,
            )
        else:
            txn.exchange_rate = Decimal("1")

    @staticmethod
    @transaction.atomic
    def add_from_object(txn: Transaction) -> Transaction:
        TransactionService._set_exchange_rate(txn)
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
    def update(form: TransactionForm) -> Transaction:
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

        TransactionService._set_exchange_rate(txn)
        return txn

    @staticmethod
    @transaction.atomic
    def delete(txn: Transaction) -> None:
        if not txn.pk:
            raise ValueError("Transaction must exist for delete")

        txn = Transaction.objects.select_for_update().get(pk=txn.pk)
        TransactionService._change_account_balance(txn.account_id, -txn.account_amount)
        txn.delete()
