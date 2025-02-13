from django.contrib import admin

from goals.models import FitnessGoal, UserFitnessGoal

# Register your models here.
admin.site.register(FitnessGoal)
admin.site.register(UserFitnessGoal)
