from django.db import transaction

from budget.models import Category


class CategoryService:
    DEFAULT_CATEGORIES_DATA = [
        {
            'name': 'Other (exp)',
            "color": "bg-danger-subtle",
            "icon": "⚪",
            "category_type": "-",
            "is_system_reserved": True,
            "is_transfer": False
        },
        {
            'name': 'Other (inc)',
            "color": "bg-success-subtle",
            "icon": "⚪",
            "category_type": "+",
            "is_system_reserved": True,
            "is_transfer": False
        },
        {
            'name': 'Transfer to',
            "color": "bg-body",
            "icon": "↗️",
            "category_type": "+",
            "is_system_reserved": True,
            "is_transfer": True
        },
        {
            'name': 'Transfer from',
            "color": "bg-body",
            "icon": "↘️",
            "category_type": "-",
            "is_system_reserved": True,
            "is_transfer": True
        },
    ]

    @staticmethod
    @transaction.atomic
    def create_default(user) -> list[Category]:
        return Category.objects.bulk_create(
            Category(user=user, **category) for category in CategoryService.DEFAULT_CATEGORIES_DATA
        )
