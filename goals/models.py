import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

class FitnessGoal(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, null=True)

    CATEGORY_CHOICES = [
        ('bmi_target', 'BMI 目标值'),
        ('weight_loss', '减重目标值'),
        ('muscle_gain', '增肌目标值'),
        ('endurance', '耐力训练'),
        ('custom', '自定义'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class UserFitnessGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    goal = models.ForeignKey(FitnessGoal, on_delete=models.CASCADE, null=False, blank=False)
    target_value = models.FloatField(null=False, blank=False)
    starting_value = models.FloatField(null=True, blank=True, default=0)  # ✅ 确保默认值为0
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ 新增字段，方便显示最新更新时间
    due_at = models.DateField(null=False, blank=False)

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')

    def clean(self):
        if self.target_value < 0:
            raise ValidationError("Target value must be greater than 0")
        if self.due_at < datetime.date.today():
            raise ValidationError("Due date must be greater than or equal to today")

    @property
    def progress(self):
        """ 计算目标进度 """
        if self.starting_value is None or self.target_value is None:
            return 0
        if self.starting_value == self.target_value:
            return 100  # 目标已完成
        if abs(self.starting_value - self.target_value) < 0.0001:
            return 100  # 避免除零错误
        progress = ((self.starting_value - self.target_value) / abs(self.starting_value - self.target_value)) * 100
        return max(0, min(progress, 100))  # 限制范围在 0%-100%
