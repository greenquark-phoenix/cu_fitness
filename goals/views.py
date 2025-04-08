from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from goals.forms import UserFitnessGoalForm
from goals.models import UserFitnessGoal, FitnessGoal, DailyCalorieLog
from datetime import timedelta, date
from django.db.models import Avg

# Delete a goal by its primary key
@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(UserFitnessGoal, pk=pk, user=request.user)
    goal.delete()
    messages.success(request, 'Goal deleted successfully!')
    return redirect('goals:user_goals')

# View to list all user goals and show progress
@login_required
def list_user_goals(request):
    available_fitness_goals = FitnessGoal.objects.all()

    # Handle goal creation form
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

    # Compute progress for each goal
    for goal in goals:
        if goal.goal.name.lower() in ["weight", "bmi"]:
            start = goal.starting_value
            target = goal.target_value
            current = goal.current_value

            total_needed = abs(target - start)

            if total_needed == 0:
                progress = 100
            elif (start > target and not (target <= current <= start)) or \
                 (start < target and not (start <= current <= target)):
                progress = 0
            else:
                actual_change = abs(current - start)
                progress = (actual_change / total_needed) * 100
        else:
            if goal.target_value > 0:
                progress = (goal.current_value / goal.target_value) * 100
            else:
                progress = 0

        goal.progress = max(0, min(round(progress, 2), 100))

    # Handle weight-specific calorie analysis
    weight_goal = next((g for g in goals if g.goal.name.lower() == "weight"), None)
    weight_context = None
    if weight_goal:
        start_weight = weight_goal.starting_value
        target_weight = weight_goal.target_value
        current_weight = weight_goal.current_value
        due_date = weight_goal.due_at
        today = date.today()
        days_remaining = max((due_date - today).days, 1)

        kcal_per_kg = 7700
        weight_diff = target_weight - start_weight
        total_kcal_needed = abs(weight_diff) * kcal_per_kg
        daily_required_change = round(total_kcal_needed / days_remaining, 2)

        if weight_diff < 0:
            goal_type = "deficit"
            required_kcal = -daily_required_change
        elif weight_diff > 0:
            goal_type = "surplus"
            required_kcal = daily_required_change
        else:
            goal_type = "maintain"
            required_kcal = 0

        recent_logs = DailyCalorieLog.objects.filter(user=user)
        if recent_logs.exists():
            net_values = [log.net_calories for log in recent_logs]
            avg_net_calories = round(sum(net_values) / len(net_values), 2) if net_values else 0
        else:
            avg_net_calories = 0

        weight_context = {
            "daily_required_kcal": required_kcal,
            "goal_type": goal_type,
            "avg_net_calories": avg_net_calories,
            "days_remaining": days_remaining,
            "behind_target": (
                (goal_type == "deficit" and avg_net_calories > required_kcal) or
                (goal_type == "surplus" and avg_net_calories < required_kcal)
            )
        }

    context = {
        'form': form,
        'available_fitness_goals': available_fitness_goals,
        'user_goals': goals,
        'weight_context': weight_context,
    }

    return render(request, 'goals/user_goals.html', context=context)

# Create a new goal
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

# Update an existing goal
@login_required
@login_required
def update_goal(request, pk):
    goal = get_object_or_404(UserFitnessGoal, pk=pk, user=request.user)

    if request.method == 'POST':
        form = UserFitnessGoalForm(request.POST, instance=goal)
        if form.is_valid():
            updated_goal = form.save(commit=False)

            # If user didn't provide a new current_value, calculate from calories
            if 'current_value' not in request.POST or request.POST['current_value'].strip() == '':
                logs = DailyCalorieLog.objects.filter(user=request.user).order_by('date')
                total_net = sum(log.net_calories for log in logs)
                weight_change = total_net / 500.0  # 500 kcal ≈ 1 kg
                updated_goal.current_value = round(goal.starting_value + weight_change, 2)

            updated_goal.save()
            messages.success(request, 'Goal progress updated successfully!')
            return redirect('goals:user_goals')
    else:
        form = UserFitnessGoalForm(instance=goal)

    return render(request, 'goals/update_goal.html', {'form': form, 'goal': goal})


# Show the net calorie trend chart over 14 days
@login_required
def net_calorie_chart(request):
    today = date.today()
    start_day = today - timedelta(days=13)

    logs = DailyCalorieLog.objects.filter(user=request.user, date__range=(start_day, today)).order_by('date')

    labels = [log.date.strftime("%Y-%m-%d") for log in logs]
    intake_data = [log.calories_intake for log in logs]
    burned_data = [log.calories_burned for log in logs]
    net_data = [log.net_calories for log in logs]

    total_intake = sum(intake_data)
    total_burned = sum(burned_data)
    total_net = total_intake - total_burned

    return render(request, 'goals/net_calorie_chart.html', {
        'labels': labels,
        'intake_data': intake_data,
        'burned_data': burned_data,
        'net_data': net_data,
        'total_intake': total_intake,
        'total_burned': total_burned,
        'total_net': total_net,
    })
