from django import forms
from goals.models import UserFitnessGoal

class UserFitnessGoalForm(forms.ModelForm):
    class Meta:
        model = UserFitnessGoal
        fields = ['goal', 'target_value', 'current_value', 'starting_value', 'due_at']  # add starting_value
        widgets = {
            'due_at': forms.DateInput(attrs={'type': 'date'}),
        }
