import datetime
import json
import random
from collections import defaultdict
from datetime import date

from django.contrib.auth.models import User

from meals.models import Meal
from schedule.models import Schedule
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
                "schedule": sub_plan.schedule,
                "exercises": WorkoutService._get_exercises(sub_plan)
            }

            result.append(sub_plan_element)
        return result

    @staticmethod
    def _get_sub_plans():
        result = []
        for sub_plan in SubPlan.objects.all():
            sub_plan_element = {
                "name": sub_plan.name,
                "focus": sub_plan.focus,
                "schedule": sub_plan.schedule,
                "exercises": WorkoutService._get_exercises(sub_plan)
            }

            result.append(sub_plan_element)
        return result

    @staticmethod
    def _get_exercises(sub_plan):
        result = []
        for exercise in sub_plan.subplanexercise_set.all():
            exercise_element = {
                "name": exercise.exercise.name,
                "unit": exercise.exercise.unit,
                "duration_or_sets": exercise.duration_or_sets,
                "calories_burned": exercise.calories_display()
            }
            result.append(exercise_element)
        return result


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


class ScheduleService:
    @staticmethod
    def create_schedule(username: str, start_date: date, num_weeks: int, meals: list, workouts: list[json]) -> None:
        user = User.objects.get(username=username)
        end_date = start_date + datetime.timedelta(days=num_weeks * 7 - 1)

        schedule, _ = Schedule.objects.get_or_create(user=user, defaults={
            'start_date': start_date,
            'end_date': end_date
        })

        schedule.start_date = start_date
        schedule.end_date = end_date
        schedule.scheduled_meals = ScheduleService._get_meal_schedule(meals, start_date, end_date)
        schedule.scheduled_workouts = ScheduleService._get_workout_schedule(workouts, start_date, end_date)
        schedule.save()

    @staticmethod
    def _get_meal_schedule(meals, start_date, end_date):
        categorized_meals = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': []
        }

        for meal_name in meals:
            try:
                meal = Meal.objects.get(meal_name=meal_name)
                mt_lower = meal.meal_type.lower()
                if mt_lower in categorized_meals:
                    categorized_meals[mt_lower].append(meal)
            except Meal.DoesNotExist:
                print('Meal not found:', meal_name)

        meal_schedule = {}

        current_date = start_date
        while current_date <= end_date:
            day_str = current_date.isoformat()
            day_entries = []

            for mt_key in ['breakfast', 'lunch', 'dinner', 'snack']:
                if categorized_meals[mt_key]:
                    chosen_meal = random.choice(categorized_meals[mt_key])
                    day_entries.append({
                        'meal_id': chosen_meal.id,
                        'meal_type': chosen_meal.meal_type,
                        'meal_category': mt_key,
                    })

            meal_schedule[day_str] = {
                'entries': day_entries
            }

            current_date += datetime.timedelta(days=1)
        return meal_schedule

    @staticmethod
    def _get_workout_schedule(workout_sub_plans: list[json], start_date, end_date):
        if not workout_sub_plans:
            return None

        plan_days = defaultdict(list)
        for sub_plan in workout_sub_plans:
            plan_days[sub_plan['day']].append(sub_plan['name'])

        plan_days_index = defaultdict(int)

        workout_schedule = {}
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime("%A")
            day = current_date.isoformat()
            current_date += datetime.timedelta(days=1)

            if day_name in plan_days:
                plan_index = plan_days_index[day_name]
                plan_days_index[day_name] = (plan_index + 1) % len(plan_days[day_name])
                work_out_name = plan_days[day_name][plan_index]

                try:
                    plan = SubPlan.objects.get(name=work_out_name)
                    plan_name = plan.name
                    plan_description = plan.schedule
                    plan_focus = plan.focus
                except SubPlan.DoesNotExist:
                    plan_name = work_out_name
                    plan_description = "No schedule info provided"
                    plan_focus = "No focus info provided"
            else:
                plan_name = "Rest Day"
                plan_description = ""
                plan_focus = ""

            workout_schedule[day] = {
                'workout': plan_name,
                'workout_description': plan_description,
                'workout_focus': plan_focus
            }

        return workout_schedule

    @staticmethod
    def format_date(date_obj):
        day_str = ScheduleService.ordinal_day(date_obj.day)
        month_str = date_obj.strftime('%B')
        year_str = str(date_obj.year)
        return f"{month_str} {day_str}, {year_str}"

    @staticmethod
    def ordinal_day(day):
        if 11 <= day <= 13:
            return f"{day}th"
        elif day % 10 == 1:
            return f"{day}st"
        elif day % 10 == 2:
            return f"{day}nd"
        elif day % 10 == 3:
            return f"{day}rd"
        else:
            return f"{day}th"
