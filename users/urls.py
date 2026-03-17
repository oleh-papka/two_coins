from django.urls import path

from . import views

urlpatterns = [
    # path('profile/edit/', views.UserEditView.as_view(), name="profile_edit"),
    path('login/', views.CustomLoginView.as_view(), name="login"),
    path('logout/', views.CustomLogoutView.as_view(), name="logout"),
    path('register/', views.CustomRegisterView.as_view(), name="register"),
]
