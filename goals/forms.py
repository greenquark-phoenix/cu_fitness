from django import forms
from .models import UserFitnessGoal, FitnessGoal

class UserFitnessGoalForm(forms.ModelForm):
    """
    表单用于用户创建和管理多个健身目标
    """
    # 目标类型字段
    goal = forms.ModelChoiceField(
        queryset=FitnessGoal.objects.filter(category__in=['bmi_target', 'weight_loss']),
        label="Target Type",
        empty_label="Select your target type",
    )

    # 目标值
    target_value = forms.FloatField(
        label="Your target value",
        min_value=0,
        help_text="Please enter your target value",
    )

    # 目标起始值（新增）
    starting_value = forms.FloatField(
        label="Starting Value (Optional)",
        required=False,
        initial=0,
        help_text="Enter your initial value (default is 0)",
    )

    # 截止日期，修改为日历选择器
    due_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Please enter your due date",
    )

    # 目标状态
    status = forms.ChoiceField(
        choices=UserFitnessGoal.STATUS_CHOICES,
        label="Status",
        initial='not_started'
    )

    class Meta:
        model = UserFitnessGoal
        fields = ['goal', 'starting_value', 'target_value', 'due_at', 'status']
