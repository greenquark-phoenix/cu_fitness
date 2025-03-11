from django.shortcuts import render
from django.db.models import Q
from .models import Meal, RecommendedDailyIntake  # <-- ADDED: Import RecommendedDailyIntake

def meal_list(request):
    meals = Meal.objects.all()

    # Retrieve filter parameters from GET request
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    duration = request.GET.get('duration', '')
    dietary_list = request.GET.getlist('dietary')  # Allow multiple dietary restrictions
    diet_type_param = request.GET.get('diet_type', '').strip().lower()  # Meal diet type

    # Filter by dynamic price range
    if price_min and price_max:
        try:
            price_min = float(price_min)
            price_max = float(price_max)
            meals = meals.filter(cost__gte=price_min, cost__lte=price_max)
        except ValueError:
            pass  # Ignore invalid values

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
        "dairy": ["milk", "yogurt", "cheese", "butter"],
        "gluten": ["wheat", "barley", "rye"],
        "shellfish": ["shrimp", "prawn", "clam", "mussel", "crab"],
        "eggs": ["egg"],
        "peanuts": ["peanut"],
        "tree nuts": ["almond", "walnut", "cashew", "pecan", "hazelnut", "pistachio", "nut"]
    }

    # Filter by dietary restrictions if provided (multiple selections)
    if dietary_list:
        q_obj = Q()
        for restriction in dietary_list:
            restriction = restriction.strip().lower()
            if restriction in dietary_map:
                for keyword in dietary_map[restriction]:
                    q_obj |= Q(ingredients__icontains=keyword)
        meals = meals.exclude(q_obj)

    # <-- ADDED: Retrieve the first (or only) RecommendedDailyIntake record
    recommended = RecommendedDailyIntake.objects.first()

    context = {
        'meals': meals,
        'recommended': recommended  # <-- ADDED: Pass it to the template
    }
    return render(request, 'meals/meal_list.html', context)
