from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("registrieren/", views.register, name="register"),
    path("ausgaben/", views.expense_list, name="expense_list"),
    path("ausgaben/neu/", views.expense_create, name="expense_create"),
]