from django import forms
from .models import Meal

class IntakeCaloriesForm(forms.Form):
    meal_items = forms.ModelMultipleChoiceField(
        queryset=Meal.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Meal Items"
    )
