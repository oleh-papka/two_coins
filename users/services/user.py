from budget.services.account import AccountService
from budget.services.category import CategoryService


class UserService:
    @staticmethod
    def create_default_data(user) -> None:
        AccountService.create_default(user)
        CategoryService.create_default(user)
