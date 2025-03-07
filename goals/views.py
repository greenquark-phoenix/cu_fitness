# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader

from goals.forms import UserFitnessGoalForm
from goals.models import UserFitnessGoal, FitnessGoal

@login_required
def list_user_goals(request):
    """View to allow a user to create a new fitness goal."""

    # Fetch available fitness goals to display
    available_fitness_goals = FitnessGoal.objects.all()

    if request.method == 'POST':
        form = UserFitnessGoalForm(request.POST)
        if form.is_valid():
            # Save the user-specific fitness goal
            user_fitness_goal = form.save(commit=False)
            user_fitness_goal.user = request.user
            user_fitness_goal.save()

            messages.success(request, 'Your fitness goal has been added successfully!')
            return redirect('user_goals')
    else:
        form = UserFitnessGoalForm()

    user = request.user
    goals = UserFitnessGoal.objects.filter(user=user)
    context = {
        'form': form,
        'available_fitness_goals': available_fitness_goals,
        'user_goals': goals
    }

    return render(request, 'goals/user_goals.html', context=context)
