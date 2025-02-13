# Create your views here.

from django.http import HttpResponse
from django.template import loader

from goals.models import UserFitnessGoal


def list_user_goals(request):
    user = request.user
    goals = UserFitnessGoal.objects.filter(user=user)
    template = loader.get_template('goals/user_goals.html')
    context = {
        'user_goals': goals
    }
    return HttpResponse(template.render(context, request))

