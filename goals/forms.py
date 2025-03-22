from django import forms
from goals.models import UserFitnessGoal


class UserFitnessGoalForm(forms.ModelForm):
    class Meta:
        model = UserFitnessGoal
        fields = ['goal', 'target_value', 'due_at']
        widgets = {
            'due_at': forms.DateInput(attrs={'type': 'date'}),
        }
