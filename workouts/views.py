from django.views.generic import ListView
from .models import WorkoutPlan

class WopListView(ListView):
    template_name = "workouts/workoutplan.html"  # Ensure this matches your template
    context_object_name = "all_wops"

    def get_queryset(self):
        return WorkoutPlan.objects.all()  # Fetch all workout plans
