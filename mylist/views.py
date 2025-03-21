# mylist/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse  
from .models import MyListItem
from meals.models import Meal

@login_required
def add_to_mylist(request, meal_id):
    """
    Adds a Meal to the user's 'mylist' if it's not already there.
    """
    if request.method == "POST":
        meal = get_object_or_404(Meal, pk=meal_id)
        MyListItem.objects.get_or_create(user=request.user, meal=meal)
    return redirect('meals_list') 

@login_required
def remove_from_mylist(request, mylist_item_id):
    """
    Removes the specified MyListItem from the user's list.
    """
    if request.method == "POST":
        item = get_object_or_404(MyListItem, pk=mylist_item_id, user=request.user)
        item.delete()
    return redirect('mylist:view_mylist')  # go back to the list page

@login_required
def view_mylist(request):
    """
    Shows all MyListItem objects for the current user.
    """
    mylist_items = MyListItem.objects.filter(user=request.user).select_related('meal')
    return render(request, 'mylist/view_mylist.html', {
        'mylist_items': mylist_items
    })

@login_required
def toggle_mylist(request):
    
    if request.method == "POST":
        meal_id = request.POST.get('meal_id')
        meal = get_object_or_404(Meal, pk=meal_id)

        existing = MyListItem.objects.filter(user=request.user, meal=meal)
        if existing.exists():
            # Remove from mylist
            existing.delete()
            return JsonResponse({"selected": False})
        else:
            # Add to mylist
            MyListItem.objects.create(user=request.user, meal=meal)
            return JsonResponse({"selected": True})

    return JsonResponse({"error": "Invalid request"}, status=400)
