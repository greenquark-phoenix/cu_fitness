from django.contrib import admin
from .models import WorkoutPlan, SubPlan, Exercise, SubPlanExercise


# Define the inline for SubPlanExercise (needed for managing exercises in sub-plans)
class SubPlanExerciseInline(admin.TabularInline):
    model = SubPlanExercise
    extra = 1


# Define the inline for SubPlans inside WorkoutPlan
class SubPlanInline(admin.TabularInline):
    model = SubPlan
    extra = 1


# Define SubPlanAdmin with a correctly referenced 'total_calories' method
class SubPlanAdmin(admin.ModelAdmin):
    inlines = [SubPlanExerciseInline]
    list_display = ("name", "workout_plan", "display_total_calories")

    def display_total_calories(self, obj):
        return obj.total_calories()

    display_total_calories.short_description = "Total Calories Burned"


# Define ExerciseAdmin
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "calorie_per_unit")


# Define WorkoutPlanAdmin
class WorkoutPlanAdmin(admin.ModelAdmin):
    inlines = [SubPlanInline]


# Register models in the Django Admin
admin.site.register(WorkoutPlan, WorkoutPlanAdmin)
admin.site.register(SubPlan, SubPlanAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(SubPlanExercise)
