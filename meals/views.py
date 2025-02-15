from django.shortcuts import render
from django.db.models import Q
from .models import Meal

def meal_list(request):
    meals = Meal.objects.all()

    # Retrieve filter parameters from GET
    price = request.GET.get('price', '')
    duration = request.GET.get('duration', '')
    # Use getlist to allow multiple dietary restrictions to be selected
    dietary_list = request.GET.getlist('dietary')
    diet_type_param = request.GET.get('diet_type', '').strip().lower()  # For meal's assigned diet type

    # Filter by price range
    if price:
        if price == 'under10':
            meals = meals.filter(cost__lt=10)
        elif price == '10to20':
            meals = meals.filter(cost__gte=10, cost__lte=20)
        elif price == 'above20':
            meals = meals.filter(cost__gt=20)

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

    context = {'meals': meals}
    return render(request, 'meals/meal_list.html', context)
