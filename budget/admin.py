from django.contrib import admin

from budget.models import Account, Category, Currency


@admin.register(Account, Currency, Category)
class BudgetAdmin(admin.ModelAdmin):
    pass
