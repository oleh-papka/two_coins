from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('accounts/', views.AccountListView.as_view(), name="account_list"),
]
