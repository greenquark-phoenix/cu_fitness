from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from django.shortcuts import render, get_object_or_404, redirect
from .models import WorkoutPlan, SubPlan


def workout_plans(request):
    """ View to list all workout plans in the correct order """
    order = [
        "Beginner Fitness Plan",
        "Weight Loss & Fat Burn Plan",
        "Functional & Mobility Plan",
        "Strength & Muscle Growth Plan",
        "Athlete Performance Plan"
    ]

    all_workout_plans = WorkoutPlan.objects.all()

    # Sort workout plans based on the defined order
    ordered_plans = sorted(all_workout_plans,
                           key=lambda plan: order.index(plan.name) if plan.name in order else len(order))

    context = {"workout_plans": ordered_plans}
    return render(request, "workouts/workout_plans.html", context=context)


def workout_plan_detail(request, plan_id):
    plan = get_object_or_404(WorkoutPlan, id=plan_id)
    sub_plans = plan.sub_plans.all()  # Retrieve sub-plans related to this workout plan

    for subplan in sub_plans:
        subplan.calories_burned = subplan.total_calories()  # Compute calories

    context = {"plan": plan, "sub_plans": sub_plans}
    return render(request, "workouts/workout_plan_detail.html", context=context)

@login_required
def registered_workout_plans(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "unregister" in request.POST:
            user_profile.selected_workout_plan = None
            user_profile.selected_sub_plan = None
        else:
            workout_plan_id = request.POST.get("workout_plan")
            sub_plan_id = request.POST.get("sub_plan")

            if workout_plan_id:
                user_profile.selected_workout_plan = WorkoutPlan.objects.get(id=workout_plan_id)
                user_profile.selected_sub_plan = None  # Reset sub-plan when changing workout plan

            if sub_plan_id:
                user_profile.selected_sub_plan = SubPlan.objects.get(id=sub_plan_id)

        user_profile.save()
        return redirect("registered_workouts")

    workout_plans = WorkoutPlan.objects.all()
    selected_workout_plan = user_profile.selected_workout_plan
    sub_plans = SubPlan.objects.filter(workout_plan=selected_workout_plan) if selected_workout_plan else None
    selected_sub_plan = user_profile.selected_sub_plan

    context = {
        "workout_plans": workout_plans,
        "selected_workout_plan": selected_workout_plan,
        "sub_plans": sub_plans,
        "selected_sub_plan": selected_sub_plan,
    }
    return render(request, "workouts/registered_workout_plans.html", context)
