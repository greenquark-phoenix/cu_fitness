import datetime
import random
import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .forms import UserFitnessGoalForm, UserFitnessProgressForm
from .models import UserFitnessGoal, FitnessGoal, UserFitnessProgress

@login_required
def goal_list(request):
    user_goals = UserFitnessGoal.objects.filter(user=request.user)
    today = datetime.date.today()

    # 1. Nearly due: within 3 days, progress < 80, not completed
    nearly_due_goals = [
        g for g in user_goals
        if 0 <= (g.due_at - today).days <= 3
        and not g.is_completed
        and g.progress < 80
    ]

    # 2. Overdue: due_at in the past, not completed
    overdue_goals = [
        g for g in user_goals
        if g.due_at < today
        and not g.is_completed
    ]

    # 3. Almost done: progress >= 80 but < 100, not completed
    almost_done_goals = [
        g for g in user_goals
        if g.progress >= 80
        and g.progress < 100
        and not g.is_completed
    ]

    return render(request, "goals/user_goals.html", {
        "user_goals": user_goals,
        "nearly_due_goals": nearly_due_goals,
        "overdue_goals": overdue_goals,
        "almost_done_goals": almost_done_goals,
    })

@login_required
def create_goal(request):
    if request.method == "POST":
        form = UserFitnessGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("goals:user_goals")
    else:
        form = UserFitnessGoalForm()
    return render(request, "goals/create_goal.html", {"form": form})

@login_required
def update_goal(request, goal_id):
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)
    if request.method == "POST":
        form = UserFitnessGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect("goals:user_goals")
    else:
        form = UserFitnessGoalForm(instance=goal)
    return render(request, "goals/update_goal.html", {"form": form, "goal": goal})

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)
    if request.method == "POST":
        goal.delete()
        return redirect("goals:user_goals")
    return render(request, "goals/delete_goal.html", {"goal": goal})

@login_required
def log_progress(request, goal_id):
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = UserFitnessProgressForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user_goal = goal
            record.save()
            # Optional: automatically mark as completed if progress >= 100
            # if goal.progress >= 100:
            #     goal.status = 'completed'
            #     goal.save()
            return redirect('goals:user_goals')
    else:
        form = UserFitnessProgressForm()
    return render(request, 'goals/log_progress.html', {
        'form': form,
        'goal': goal
    })

@login_required
def recommend_goals(request):
    user = request.user
    existing = UserFitnessGoal.objects.filter(user=user)
    possible = FitnessGoal.objects.exclude(id__in=existing.values_list('goal_id', flat=True))
    recommended = random.sample(list(possible), min(3, len(possible)))
    return render(request, "goals/recommend_goals.html", {"recommended_goals": recommended})

@login_required
def goal_progress_notification(request):
    user = request.user
    nearing_completion = [
        g for g in UserFitnessGoal.objects.filter(user=user)
        if g.progress >= 80 and g.status == 'in_progress'
    ]
    return render(request, "goals/goal_progress_notification.html", {
        "nearing_completion_goals": nearing_completion
    })

@login_required
def create_goal_from_assistant(request):
    if request.method == "POST":
        user_input = request.POST.get("text", "")
        weight_loss_match = re.search(r"lose (\d+)kg", user_input)
        time_match = re.search(r"(\d+) months later", user_input)

        if weight_loss_match and time_match:
            weight_loss = int(weight_loss_match.group(1))
            months = int(time_match.group(1))
            fitness_goal = FitnessGoal.objects.filter(name="Weight Loss Target").first()
            if not fitness_goal:
                return JsonResponse({"error": "No matching FitnessGoal found."})

            new_goal = UserFitnessGoal.objects.create(
                user=request.user,
                goal=fitness_goal,
                initial_value=0,
                target_value=weight_loss,
                due_at=datetime.date.today() + datetime.timedelta(days=30 * months),
                status="not_started"
            )
            return JsonResponse({
                "message": f"Goal created: lose {weight_loss} kg in {months} months.",
                "goal_id": new_goal.id
            })
        return JsonResponse({
            "error": "Unable to parse the goal. Please describe in clearer language."
        })
