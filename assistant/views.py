from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
@login_required
def assistant_view(request):
    return render(request, "assistant/chat/chat.html")

@login_required
def new_assistant_view(request):
    if "messages" in request.session:
        del request.session["messages"]

    if "thread_id" in request.session:
        del request.session["thread_id"]

    return JsonResponse({"status": "success"})