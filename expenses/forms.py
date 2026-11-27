from django import forms

from .models import Budget, Expense


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