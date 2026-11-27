from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from .forms import ExpenseForm

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import redirect, render

from .models import Category

DEFAULT_CATEGORIES = ["Essen", "Wohnen", "Transport", "Freizeit", "Sonstiges"]


@login_required
def home(request):
    categories = request.user.categories.all()
    return render(request, "expenses/home.html", {"categories": categories})


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
def expense_list(request):
    today = timezone.localdate()
    expenses = (
        request.user.expenses
        .filter(date__year=today.year, date__month=today.month)
        .select_related("category")
    )
    total = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    return render(
        request,
        "expenses/expense_list.html",
        {"expenses": expenses, "total": total, "today": today},
    )