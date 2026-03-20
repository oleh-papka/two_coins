from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('accounts/', views.AccountListView.as_view(), name="account_list"),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name="account_update"),
    path('accounts/add/', views.AccountCreateView.as_view(), name="account_add"),
    path('categories/', views.CategoryListView.as_view(), name="category_list"),
]
