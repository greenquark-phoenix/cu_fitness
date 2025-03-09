from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.
@login_required
def assistant_view(request):
    return render(request, "assistant/chat/chat.html")
