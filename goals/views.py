from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime
import random
import re

from .forms import UserFitnessGoalForm, UserFitnessProgressForm
from .models import UserFitnessGoal, FitnessGoal, UserFitnessProgress


@login_required
def goal_list(request):
    """Display all fitness goals for the current user."""
    user_goals = UserFitnessGoal.objects.filter(user=request.user)
    return render(request, "goals/user_goals.html", {"user_goals": user_goals})


@login_required
def create_goal(request):
    """Allow users to create multiple types of goals."""
    if request.method == "POST":
        form = UserFitnessGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("goals:user_goals")
        else:
            print(form.errors)
    else:
        form = UserFitnessGoalForm()

    return render(request, "goals/create_goal.html", {"form": form})


@login_required
def update_goal(request, goal_id):
    """Allow users to update a goal, e.g. modify value, due date, status, etc."""
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)

    if request.method == "POST":
        form = UserFitnessGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect("goals:user_goals")
        else:
            print(form.errors)
    else:
        form = UserFitnessGoalForm(instance=goal)

    return render(request, "goals/update_goal.html", {"form": form, "goal": goal})


@login_required
def delete_goal(request, goal_id):
    """Allow users to delete a goal."""
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)

    if request.method == "POST":
        goal.delete()
        return redirect("goals:user_goals")

    return render(request, "goals/delete_goal.html", {"goal": goal})


@login_required
def recommend_goals(request):
    """Recommend new goals based on the user's history."""
    user = request.user
    existing_goals = UserFitnessGoal.objects.filter(user=user)
    possible_goals = FitnessGoal.objects.exclude(id__in=existing_goals.values_list('goal_id', flat=True))
    recommended_goals = random.sample(list(possible_goals), min(3, len(possible_goals)))

    return render(request, "goals/recommend_goals.html", {"recommended_goals": recommended_goals})


@login_required
def goal_progress_notification(request):
    """Notify users that they are close to achieving their goals."""
    user = request.user
    # This depends on progress >= 80
    nearing_completion_goals = [
        g for g in UserFitnessGoal.objects.filter(user=user)
        if g.progress >= 80 and g.status == 'in_progress'
    ]

    return render(
        request,
        "goals/goal_progress_notification.html",
        {"nearing_completion_goals": nearing_completion_goals}
    )


@login_required
def create_goal_from_assistant(request):
    """
    Allow users to create a goal directly via AI.
    Example input: "lose 5kg in 2 months later"
    """
    if request.method == "POST":
        user_input = request.POST.get("text", "")

        # e.g., "lose 5kg in 2 months later"
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


@login_required
def log_progress(request, goal_id):
    """
    Let the user log (check in) their current value for a specific goal.
    """
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)

    if request.method == 'POST':
        form = UserFitnessProgressForm(request.POST)
        if form.is_valid():
            progress_record = form.save(commit=False)
            progress_record.user_goal = goal
            progress_record.save()
            # Optionally, update status automatically if progress >= 100:
            # if goal.progress >= 100:
            #     goal.status = 'completed'
            #     goal.save()

            return redirect('goals:user_goals')
        else:
            print(form.errors)
    else:
        form = UserFitnessProgressForm()

    return render(request, 'goals/log_progress.html', {
        'form': form,
        'goal': goal
    })
