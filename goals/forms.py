from django import forms
from .models import UserFitnessGoal, FitnessGoal

class UserFitnessGoalForm(forms.ModelForm):
    """
    A form for users to create and manage multiple fitness goals.
    """

    # Goal type field
    goal = forms.ModelChoiceField(
        queryset=FitnessGoal.objects.filter(category__in=['bmi_target', 'weight_loss']),
        label="Target Type",
        empty_label="Select your target type",
    )

    # Target value
    target_value = forms.FloatField(
        label="Your target value",
        min_value=0,
        help_text="Please enter your target value",
    )

    # Starting value
    starting_value = forms.FloatField(
        label="Starting Value (Optional)",
        required=False,
        initial=0,
        help_text="Enter your initial value (default is 0)",
    )

    # Due date (using a date selector widget)
    due_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Please enter your due date",
    )

    # Goal status
    status = forms.ChoiceField(
        choices=UserFitnessGoal.STATUS_CHOICES,
        label="Status",
        initial='not_started'
    )

    class Meta:
        model = UserFitnessGoal
        fields = ['goal', 'starting_value', 'target_value', 'due_at', 'status']
