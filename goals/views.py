from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime, random, re

from goals.models import UserFitnessGoal


@login_required
def goal_list(request):
    """ 显示用户所有的健身目标 """
    user_goals = UserFitnessGoal.objects.filter(user=request.user)
    return render(request, "goals/user_goals.html", {"user_goals": user_goals})


@login_required
def create_goal(request):
    """ 允许用户创建多个不同类型的目标，而不是覆盖已有目标 """
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
    """ 允许用户更新目标，例如修改目标值、截止日期、状态等 """
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
    """ 允许用户删除目标 """
    goal = get_object_or_404(UserFitnessGoal, id=goal_id, user=request.user)

    if request.method == "POST":
        goal.delete()
        return redirect("goals:user_goals")

    return render(request, "goals/delete_goal.html", {"goal": goal})


@login_required
def recommend_goals(request):
    """ 根据用户历史数据推荐新目标 """
    user = request.user
    existing_goals = UserFitnessGoal.objects.filter(user=user)
    possible_goals = FitnessGoal.objects.exclude(id__in=existing_goals.values_list('goal_id', flat=True))
    recommended_goals = random.sample(list(possible_goals), min(3, len(possible_goals)))

    return render(request, "goals/recommend_goals.html", {"recommended_goals": recommended_goals})


@login_required
def goal_progress_notification(request):
    """ 提示用户即将达成目标 """
    user = request.user
    nearing_completion_goals = UserFitnessGoal.objects.filter(user=user, progress__gte=80, status='in_progress')

    return render(request, "goals/goal_progress_notification.html", {"nearing_completion_goals": nearing_completion_goals})


@login_required
def create_goal_from_assistant(request):
    """ 允许用户通过 AI 直接创建目标 """
    if request.method == "POST":
        user_input = request.POST.get("text", "")

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

            return JsonResponse({"message": f"目标已创建：减肥 {weight_loss}kg，目标时间 {months} 个月后。", "goal_id": new_goal.id})

        return JsonResponse({"error": "无法解析目标，请用更清晰的语言描述。"})
