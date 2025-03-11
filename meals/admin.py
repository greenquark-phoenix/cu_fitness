from django.contrib import admin
from .models import Meal, Ingredient, MealIngredient, RecommendedDailyIntake

class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1

class MealAdmin(admin.ModelAdmin):
    inlines = [MealIngredientInline]
    list_display = ('meal_name', 'meal_type', 'diet_type', 'cooking_duration', 'cost', 'total_calories')

admin.site.register(Meal, MealAdmin)
admin.site.register(Ingredient)
admin.site.register(RecommendedDailyIntake)
