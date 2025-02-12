from django.shortcuts import render, redirect
from django.contrib.auth import login

from users.forms import SignupForm


# Create your views here.
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")  # Change "home" to your desired redirect URL
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})
