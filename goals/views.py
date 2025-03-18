from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime, random, re

# Make sure you have these imports if they are missing:
from .models import UserFitnessGoal, FitnessGoal
from .forms import UserFitnessGoalForm

@login_required
def goal_list(request):
    """
    Display all fitness goals belonging to the user.
    """
    user_goals = UserFitnessGoal.objects.filter(user=request.user)
    return render(request, "goals/user_goals.html", {"user_goals": user_goals})

@login_required
def create_goal(request):
    """
    Allow users to create multiple types of goals instead of overwriting existing ones.
    """
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
    """
    Allow users to update goals, such as modifying target value, due date, status, etc.
    """
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
    """
    Allow users to delete a goal.
    """
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)

    if request.method == "POST":
        goal.delete()
        return redirect("goals:user_goals")

    return render(request, "goals/delete_goal.html", {"goal": goal})

@login_required
def recommend_goals(request):
    """
    Recommend new goals based on the user's historical data.
    """
    user = request.user
    existing_goals = UserFitnessGoal.objects.filter(user=user)
    possible_goals = FitnessGoal.objects.exclude(id__in=existing_goals.values_list('goal_id', flat=True))
    recommended_goals = random.sample(list(possible_goals), min(3, len(possible_goals)))

    return render(request, "goals/recommend_goals.html", {"recommended_goals": recommended_goals})

@login_required
def goal_progress_notification(request):
    """
    Notify the user if they are close to achieving their goal (>= 80% progress).
    """
    user = request.user
    nearing_completion_goals = UserFitnessGoal.objects.filter(user=user, progress__gte=80, status='in_progress')

    return render(request, "goals/goal_progress_notification.html", {"nearing_completion_goals": nearing_completion_goals})

@login_required
def create_goal_from_assistant(request):
    """
    Allow users to directly create a goal via AI.
    """
    if request.method == "POST":
        user_input = request.POST.get("text", "")

        # Matches "减肥 (\d+)kg" and "(\d+)个月后" in Chinese.
        weight_loss_match = re.search(r"减肥 (\d+)kg", user_input)
        time_match = re.search(r"(\d+)个月后", user_input)

        if weight_loss_match and time_match:
            weight_loss = int(weight_loss_match.group(1))
            months = int(time_match.group(1))

            new_goal = UserFitnessGoal.objects.create(
                user=request.user,
                goal=FitnessGoal.objects.get(name="Weight Loss Target"),
                target_value=weight_loss,
                due_at=datetime.date.today() + datetime.timedelta(days=30 * months),
                status="not_started"
            )

            return JsonResponse({"message": f"Goal created: lose {weight_loss} kg, target time {months} months from now.",
                                 "goal_id": new_goal.id})

        return JsonResponse({"error": "Unable to parse the goal. Please use clearer language."})

def bmi_calculator(request):
    """
    A simple BMI calculator view.
    """
    bmi_result = None  # Used to store the calculated BMI
    height = None
    weight = None

    if request.method == 'POST':
        # Get the submitted values, default to 0 to avoid errors
        height = float(request.POST.get('height', 0))
        weight = float(request.POST.get('weight', 0))

        # Ensure height is not 0
        if height != 0:
            # Calculate BMI
            bmi_result = round(weight / ((height / 100) * (height / 100)), 2)

    # Render the template and pass the result
    return render(request, 'goals/bmi_calculator.html', {
        'bmi_result': bmi_result,
        'height': height,
        'weight': weight
    })
