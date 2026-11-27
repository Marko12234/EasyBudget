from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("registrieren/", views.register, name="register"),
    path("ausgaben/", views.expense_list, name="expense_list"),
    path("ausgaben/neu/", views.expense_create, name="expense_create"),
    path("ausgaben/<int:year>/<int:month>/", views.expense_list, name="expense_list_month"),
    path("budget/", views.budget_edit, name="budget_edit"),
]