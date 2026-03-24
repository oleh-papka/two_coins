from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('accounts/', views.AccountListView.as_view(), name="account_list"),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name="account_update"),
    path('accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name="account_delete"),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name="account_detail"),
    path('accounts/add/', views.AccountCreateView.as_view(), name="account_add"),
    path('categories/', views.CategoryListView.as_view(), name="category_list"),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name="category_update"),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name="category_delete"),
    path('categories/add/', views.CategoryCreateView.as_view(), name="category_add"),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name="category_detail"),
    path('transactions/', views.TransactionListView.as_view(), name="transaction_list"),
    path('transactions/add/', views.TransactionCreateView.as_view(), name="transaction_add"),
    path('transactions/<int:pk>/update/', views.TransactionUpdateView.as_view(), name="transaction_update"),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name="transaction_delete"),
]
