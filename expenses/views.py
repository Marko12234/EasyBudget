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