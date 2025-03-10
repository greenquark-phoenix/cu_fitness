from django.contrib import admin
from .models import WorkoutPlan, SubPlan

class SubPlanInline(admin.TabularInline):  # Allows adding sub-plans inside the workout plan admin
    model = SubPlan
    extra = 1

class WorkoutPlanAdmin(admin.ModelAdmin):
    inlines = [SubPlanInline]

admin.site.register(WorkoutPlan, WorkoutPlanAdmin)
admin.site.register(SubPlan)
