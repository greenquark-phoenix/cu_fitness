
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import loader
from django.shortcuts import get_object_or_404
from goals.forms import UserFitnessGoalForm
from goals.models import UserFitnessGoal, FitnessGoal
from .models import FitnessGoal, UserFitnessGoal, DailyCalorieLog
from datetime import timedelta, date
from django.db.models import Avg

@login_required
def list_user_goals(request):
    # Fetch all available fitness goals
    available_fitness_goals = FitnessGoal.objects.all()

    if request.method == 'POST':
        form = UserFitnessGoalForm(request.POST)
        if form.is_valid():
            user_fitness_goal = form.save(commit=False)
            user_fitness_goal.user = request.user
            user_fitness_goal.save()

            messages.success(request, 'Your fitness goal has been added successfully!')
            return redirect('goals:user_goals')
    else:
        form = UserFitnessGoalForm()

    user = request.user
    goals = UserFitnessGoal.objects.filter(user=user)

    # Add progress percentage for each goal
    for goal in goals:
        if goal.target_value > 0:
            progress = (goal.current_value / goal.target_value) * 100
            goal.progress = progress if progress <= 100 else 100
        else:
            goal.progress = 0

    # Analyze weight-related calorie requirement
    weight_goal = next((g for g in goals if g.goal.name.lower() == "weight"), None)
    weight_context = None
    if weight_goal:
        start_weight = weight_goal.current_value
        target_weight = weight_goal.target_value
        due_date = weight_goal.due_at
        today = date.today()
        days_remaining = max((due_date - today).days, 1)

        weight_to_lose = max(start_weight - target_weight, 0)
        kcal_per_kg = 7700  # Approximate kcal to burn 1kg of fat
        total_deficit_needed = weight_to_lose * kcal_per_kg
        daily_required_deficit = round(total_deficit_needed / days_remaining, 2)

        # Compute average net calorie of the user
        recent_logs = DailyCalorieLog.objects.filter(user=user)
        if recent_logs.exists():
            net_values = [log.net_calories for log in recent_logs]
            avg_net_calories = round(sum(net_values) / len(net_values), 2) if net_values else 0
        else:
            avg_net_calories = 0

        weight_context = {
            "daily_required_deficit": daily_required_deficit,
            "avg_net_calories": avg_net_calories,
            "days_remaining": days_remaining,
            "behind_target": avg_net_calories > -daily_required_deficit,
        }

    context = {
        'form': form,
        'available_fitness_goals': available_fitness_goals,
        'user_goals': goals,
        'weight_context': weight_context,
    }

    return render(request, 'goals/user_goals.html', context=context)


@login_required
def create_goal(request):
    if request.method == 'POST':
        form = UserFitnessGoalForm(request.POST)
        if form.is_valid():
            user_goal = form.save(commit=False)
            user_goal.user = request.user
            user_goal.save()
            messages.success(request, 'Goal created successfully!')
            return redirect('goals:user_goals')
    else:
        form = UserFitnessGoalForm()

    return render(request, 'goals/create_goal.html', {'form': form})


@login_required
def update_goal(request, pk):
    goal = get_object_or_404(UserFitnessGoal, pk=pk, user=request.user)

    if request.method == 'POST':
        form = UserFitnessGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal progress updated successfully!')
            return redirect('goals:user_goals')
    else:
        form = UserFitnessGoalForm(instance=goal)

    return render(request, 'goals/update_goal.html', {'form': form, 'goal': goal})


@login_required
def net_calorie_chart(request):
    today = date.today()
    start_day = today - timedelta(days=13)

    logs = DailyCalorieLog.objects.filter(user=request.user, date__range=(start_day, today)).order_by('date')

    labels = [log.date.strftime("%Y-%m-%d") for log in logs]
    intake_data = [log.calories_intake for log in logs]
    burned_data = [log.calories_burned for log in logs]
    net_data = [log.net_calories for log in logs]

    return render(request, 'goals/net_calorie_chart.html', {
        'labels': labels,
        'intake_data': intake_data,
        'burned_data': burned_data,
        'net_data': net_data,
    })
