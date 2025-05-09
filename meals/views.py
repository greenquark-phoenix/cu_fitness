from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Meal, RecommendedDailyIntake, UserMealSelection
from schedule.models import MyList


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
        "dairy": ["milk", "Greek yogurt", "yogurt", "cheese", "butter", "Parmesan Cheese", "Mozzarella Cheese", "Feta Cheese"],
        "gluten": ["wheat", "barley", "rye", "Breadcrumbs", "Whole Wheat Couscous", "Whole Wheat Flour", "Whole Wheat Tortilla", "Whole Wheat Pita", "Whole-grain Bread", "Pasta", "Whole Grain Cereal"],
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

    # Retrieve the first (or only) RecommendedDailyIntake record
    recommended = RecommendedDailyIntake.objects.first()

    # Get selected meal IDs from MyList if the user is authenticated
    selected_meal_ids = []
    if request.user.is_authenticated:
        mylist, _ = MyList.objects.get_or_create(user=request.user)
        selected_meal_ids = list(mylist.meals.values_list('id', flat=True))

    context = {
        'meals': meals,
        'recommended': recommended,
        'selected_meal_ids': selected_meal_ids,
    }
    return render(request, 'meals/meal_list.html', context)

@login_required
@require_POST
def toggle_meal_selection(request):
    meal_id = request.POST.get('meal_id')
    if not meal_id:
        return JsonResponse({'error': 'No meal_id provided'}, status=400)

    meal = get_object_or_404(Meal, pk=meal_id)
    mylist, _ = MyList.objects.get_or_create(user=request.user)

    if meal in mylist.meals.all():
        mylist.meals.remove(meal)
        selected = False
    else:
        mylist.meals.add(meal)
        selected = True

    return JsonResponse({'selected': selected})

@login_required
def intake_calories(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist('meal_items')

        #  Force save to trigger signal
        for meal in Meal.objects.all():
            selection, _ = UserMealSelection.objects.get_or_create(user=request.user, meal=meal)
            selection.selected = str(meal.id) in selected_ids
            selection.save()  #  This triggers the signal

        return redirect('goals:net_calorie_chart')

    else:
        total_calories = None

    meals = Meal.objects.all()
    context = {
        'breakfast_items': meals.filter(meal_type__iexact='breakfast'),
        'lunch_items': meals.filter(meal_type__iexact='lunch'),
        'dinner_items': meals.filter(meal_type__iexact='dinner'),
        'snack_items': meals.filter(meal_type__iexact='snack'),
        'total_calories': total_calories,
    }

    return render(request, 'meals/intake_calories.html', context)