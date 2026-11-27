from django import forms

from .models import Budget, Category, Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["amount", "category", "date", "description"]
        labels = {
            "amount": "Betrag (CHF)",
            "category": "Kategorie",
            "date": "Datum",
            "description": "Beschreibung",
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = user.categories.all()

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["amount"]
        labels = {"amount": "Budget (CHF)"}

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        labels = {"name": "Neue Kategorie"}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if self.user.categories.filter(name__iexact=name).exists():
            raise forms.ValidationError("Diese Kategorie existiert bereits.")
        return name