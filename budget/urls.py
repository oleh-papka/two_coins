from django.urls import path

from .views.account import AccountListView, AccountUpdateView, AccountDeleteView, AccountDetailView, AccountCreateView
from .views.category import CategoryListView, CategoryUpdateView, CategoryDeleteView, CategoryCreateView, \
    CategoryDetailView
from .views.dashboard import DashboardView
from .views.transaction import TransactionListView, TransactionCreateView, TransactionUpdateView, TransactionDeleteView

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path('accounts/', AccountListView.as_view(), name="account_list"),
    path('accounts/<int:pk>/update/', AccountUpdateView.as_view(), name="account_update"),
    path('accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name="account_delete"),
    path('accounts/<int:pk>/', AccountDetailView.as_view(), name="account_detail"),
    path('accounts/add/', AccountCreateView.as_view(), name="account_add"),
    path('categories/', CategoryListView.as_view(), name="category_list"),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name="category_update"),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name="category_delete"),
    path('categories/add/', CategoryCreateView.as_view(), name="category_add"),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name="category_detail"),
    path('transactions/', TransactionListView.as_view(), name="transaction_list"),
    path('transactions/add/', TransactionCreateView.as_view(), name="transaction_add"),
    path('transactions/<int:pk>/update/', TransactionUpdateView.as_view(), name="transaction_update"),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name="transaction_delete"),
]
