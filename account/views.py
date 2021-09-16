from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from account.forms import CustomUserCreationForm


def dashboard(request):
    return render(request, "account/dashboard.html")


def register(request):
    if request.method == "GET":
        return render(
            request, "account/register.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("task_app:index"))