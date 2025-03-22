from django.shortcuts import render
from django.db.models import Q
from .models import Meal, RecommendedDailyIntake, UserMealSelection
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import IntakeCaloriesForm

def meal_list(request):
    meals = Meal.objects.all()

    # Retrieve filter parameters from GET request
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    duration = request.GET.get('duration', '')
    dietary_list = request.GET.getlist('dietary')  # multiple dietary restrictions
    diet_type_param = request.GET.get('diet_type', '').strip().lower()

    # Filter by dynamic price range
    if price_min and price_max:
        try:
            price_min_val = float(price_min)
            price_max_val = float(price_max)
            meals = meals.filter(cost__gte=price_min_val, cost__lte=price_max_val)
        except ValueError:
            pass  # ignore invalid values

    # Filter by cooking duration
    if duration:
        if duration == 'under15':
            meals = meals.filter(cooking_duration__lt=15)
        elif duration == '15to30':
            meals = meals.filter(cooking_duration__gte=15, cooking_duration__lte=30)
        elif duration == 'above30':
            meals = meals.filter(cooking_duration__gt=30)

    # Filter by the meal's assigned diet type (non-veg, veg, or vegan)
    if diet_type_param:
        meals = meals.filter(diet_type=diet_type_param)

    # Mapping of dietary restrictions to keywords for exclusion
    dietary_map = {
        "dairy": [
            "milk", "Greek yogurt", "yogurt", "cheese", "butter",
            "Parmesan Cheese", "Mozzarella Cheese", "Feta Cheese"
        ],
        "gluten": [
            "wheat", "barley", "rye", "Breadcrumbs", "Whole Wheat Couscous",
            "Whole Wheat Flour", "Whole Wheat Tortilla", "Whole Wheat Pita",
            "Whole-grain Bread", "Pasta", "Whole Grain Cereal"
        ],
        "shellfish": ["shrimp", "prawn", "clam", "mussel", "crab"],
        "eggs": ["egg"],
        "peanuts": ["peanut"],
        "tree nuts": ["almond", "walnut", "cashew", "pecan", "hazelnut", "pistachio", "nut"]
    }

    # Filter by dietary restrictions (exclusion)
    if dietary_list:
        q_obj = Q()
        for restriction in dietary_list:
            restriction = restriction.strip().lower()
            if restriction in dietary_map:
                for keyword in dietary_map[restriction]:
                    q_obj |= Q(ingredients__icontains=keyword)
        meals = meals.exclude(q_obj)

    # Retrieve the first (or only) RecommendedDailyIntake record
    recommended = RecommendedDailyIntake.objects.first()

    context = {
        'meals': meals,
        'recommended': recommended
    }
    return render(request, 'meals/meal_list.html', context)

def intake_calories(request):
    meals = Meal.objects.all()

    # Categorize the meals by type
    breakfast_items = meals.filter(meal_type="breakfast")
    lunch_items = meals.filter(meal_type="lunch")
    dinner_items = meals.filter(meal_type="dinner")
    snack_items = meals.filter(meal_type="snack")

    total_calories = 0

    if request.method == "POST":
        selected_meal_ids = request.POST.getlist("meal_items")  # user-selected meals
        selected_meals = Meal.objects.filter(id__in=selected_meal_ids)
        total_calories = sum(meal.dv_calories for meal in selected_meals)

    return render(request, "meals/intake_calories.html", {
        "breakfast_items": breakfast_items,
        "lunch_items": lunch_items,
        "dinner_items": dinner_items,
        "snack_items": snack_items,
        "total_calories": total_calories,
    })

@login_required
@require_POST
def toggle_meal_selection(request):
    """
    Toggles the user's selection of a meal (adding/removing it in their MyList).
    """
    meal_id = request.POST.get('meal_id')
    if not meal_id:
        return JsonResponse({'error': 'No meal_id provided'}, status=400)

    try:
        meal = Meal.objects.get(id=meal_id)
    except Meal.DoesNotExist:
        return JsonResponse({'error': 'Meal does not exist'}, status=404)

    selection, created = UserMealSelection.objects.get_or_create(user=request.user, meal=meal)
    selection.selected = not selection.selected
    selection.save()

    return JsonResponse({'selected': selection.selected})
