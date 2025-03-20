from datetime import date
import json

from django.contrib.auth.models import User

from meals.models import Meal
from users.models import UserProfile
from workouts.models import SubPlan


class ProfileService:

    @staticmethod
    def get_basic_info(username: str) -> str:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
        gender = user_profile.gender
        height = user_profile.height
        weight = user_profile.current_weight
        birth_date = user_profile.birth_date
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return f"gender: {gender}, height: {height} cm, weight: {weight} Kg, and age: {age} years."

    @staticmethod
    def get_dietary_info(username: str) -> str:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
        allergies = user_profile.allergies if not None else "None"
        dietary_preferences = user_profile.dietary_preferences if not None else "None"
        return f"Allergies: {allergies}, Dietary Preferences: {dietary_preferences}"


class WorkoutService:
    @staticmethod
    def get_available_workouts() -> json:
        result = []

        for sub_plan in SubPlan.objects.all():
            sub_plan_element = {
                "name": sub_plan.name,
                "focus": sub_plan.focus,
                "schedule": sub_plan.schedule
            }

            exercises = []
            for exercise in sub_plan.subplanexercise_set.all():
                exercise_element = {
                    "name": exercise.exercise.name,
                    "unit": exercise.exercise.unit,
                    "duration_or_sets": exercise.duration_or_sets,
                    "calories_burned": exercise.calories_display()
                }
                exercises.append(exercise_element)

            sub_plan_element["exercises"] = exercises
            result.append(sub_plan_element)

        return json.dumps(result)

class NutritionService:
    @staticmethod
    def get_available_meals() -> json:
        result = []

        for meal in Meal.objects.all():
            meal_element = {
                "name": meal.meal_name,
                "type": meal.meal_type,
                "ingredients": meal.ingredients,
                "cost": "$" + str(meal.cost),
                "cooking_duration": meal.cooking_duration,
                "diet_type": meal.diet_type
            }
            result.append(meal_element)

        return json.dumps(result)
