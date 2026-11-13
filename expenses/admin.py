from django.contrib import admin

from .models import Budget, Category, Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["date", "amount", "category", "description", "user"]
    list_filter = ["category", "date"]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["year", "month", "amount", "user"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user"]