from django.db import transaction

from budget.models import Category
from budget.services.transaction import TransactionService


class CategoryService:

    @staticmethod
    @transaction.atomic
    def delete(category: Category):
        txns = category.transaction_set.all()

        for txn in txns:
            TransactionService.delete_transaction(txn)

        category.delete()
