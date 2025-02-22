from django.contrib.auth import login
from django.shortcuts import render, redirect

from users.forms import SignupForm


# Create your views here.
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")  # Change "home" to your desired redirect URL
    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})