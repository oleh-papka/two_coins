import datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from budget.models import Account, Transaction, Category, Transfer
from budget.services.transaction import TransactionService


class TransferService:

    @staticmethod
    @transaction.atomic
    def create(account_from: Account,
               amount_from: Decimal,
               account_to: Account,
               amount_to: Decimal,
               performed_date: datetime.date = None):
        if account_from.pk == account_to.pk:
            raise ValueError("Cannot transfer to the same account.")

        user = account_from.user
        transfer_categories = {
            c.category_type: c
            for c in Category.objects.transfer()
        }
        try:
            expense_category = transfer_categories[Category.CategoryType.EXPENSE]
            income_category = transfer_categories[Category.CategoryType.INCOME]
        except KeyError:
            raise ValueError("Transfer categories are not configured correctly.")

        if performed_date is None:
            performed_date = timezone.localdate()

        txn_from = Transaction(
            account=account_from,
            currency=account_from.currency,
            category=expense_category,
            amount=amount_from,
            account_amount=amount_from,
            performed_date=performed_date,
            user=user
        )
        TransactionService.add_from_object(txn_from)

        txn_to = Transaction(
            account=account_to,
            currency=account_to.currency,
            category=income_category,
            amount=amount_to,
            account_amount=amount_to,
            performed_date=performed_date,
            user=user
        )
        TransactionService.add_from_object(txn_to)

        return Transfer.objects.create(from_account=account_from,
                                       txn_from=txn_from,
                                       to_account=account_to,
                                       txn_to=txn_to)

    @staticmethod
    @transaction.atomic
    def delete(transfer: Transfer) -> None:
        if not transfer.pk:
            raise ValueError("Transfer must exist for delete")

        transfer = (
            Transfer.objects
            .select_related("txn_from", "txn_to")
            .select_for_update()
            .get(pk=transfer.pk)
        )

        txn_from = transfer.txn_from
        txn_to = transfer.txn_to

        transfer.delete()

        TransactionService.delete(txn_from)
        TransactionService.delete(txn_to)
