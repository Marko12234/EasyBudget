from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from datetime import date, timedelta

from django.http import Http404

from decimal import Decimal

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import BudgetForm, CategoryForm, ExpenseForm
from .models import Category

DEFAULT_CATEGORIES = ["Essen", "Wohnen", "Transport", "Freizeit", "Sonstiges"]


def month_expenses(user, year, month):
    return user.expenses.filter(date__year=year, date__month=month)


def month_total(user, year, month):
    total = month_expenses(user, year, month).aggregate(total=Sum("amount"))["total"]
    return total or Decimal("0")


@login_required
def home(request):
    today = timezone.localdate()
    budget = request.user.budgets.filter(year=today.year, month=today.month).first()
    total = month_total(request.user, today.year, today.month)

    percent = None
    bar_width = 0
    status = None
    remaining = None

    if budget:
        percent = round(total / budget.amount * 100)
        bar_width = min(percent, 100)
        remaining = budget.amount - total
        if percent >= 100:
            status = "danger"
        elif percent >= 80:
            status = "warning"
        else:
            status = "ok"

    context = {
        "today": today,
        "budget": budget,
        "total": total,
        "percent": percent,
        "bar_width": bar_width,
        "status": status,
        "remaining": remaining,
    }
    return render(request, "expenses/home.html", context)


@login_required
def budget_edit(request):
    today = timezone.localdate()
    budget = request.user.budgets.filter(year=today.year, month=today.month).first()

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.year = today.year
            budget.month = today.month
            budget.save()
            return redirect("home")
    else:
        form = BudgetForm(instance=budget)

    return render(request, "expenses/budget_form.html", {"form": form, "today": today})


@login_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect("expense_list")
    else:
        form = ExpenseForm(user=request.user)

    return render(request, "expenses/expense_form.html", {"form": form})


@login_required
def expense_list(request, year=None, month=None):
    today = timezone.localdate()
    year = year or today.year
    month = month or today.month

    try:
        current = date(year, month, 1)
    except ValueError:
        raise Http404("Ungültiger Monat")

    prev_month = (current - timedelta(days=1)).replace(day=1)
    next_month = (current + timedelta(days=32)).replace(day=1)

    expenses = month_expenses(request.user, year, month).select_related("category")
    total = month_total(request.user, year, month)

    context = {
        "expenses": expenses,
        "total": total,
        "current": current,
        "prev_month": prev_month,
        "next_month": next_month,
        "is_current_month": (year, month) == (today.year, today.month),
    }
    return render(request, "expenses/expense_list.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                Category.objects.bulk_create(
                    [Category(user=user, name=name) for name in DEFAULT_CATEGORIES]
                )
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})

@login_required
def category_list(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Kategorie "{category.name}" angelegt.')
            return redirect("category_list")
    else:
        form = CategoryForm(user=request.user)

    categories = request.user.categories.all()
    return render(
        request,
        "expenses/category_list.html",
        {"form": form, "categories": categories},
    )


@login_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    try:
        category.delete()
        messages.success(request, f'Kategorie "{category.name}" gelöscht.')
    except ProtectedError:
        messages.error(
            request,
            f'"{category.name}" hat noch Ausgaben und kann nicht gelöscht werden.',
        )
    return redirect("category_list")