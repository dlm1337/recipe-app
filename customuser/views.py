from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def register_user(request):
    form = CustomUserCreationForm()  # Move the form creation outside the if-else block

    if request.method == "POST":
        submit_type = request.POST.get("submit_type")

        if submit_type == "register_btn":
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Account created successfully. Please login.")
                # Redirect to a success page or login page after registration
                return redirect("login")

    return render(request, "customuser/register.html", {"form": form})


@login_required
def your_profile(request):
    if request.method == "POST":
        submit_type = request.POST.get("submit_type")

        if submit_type == "profile_update_btn":
            form = CustomUserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Your profile has been updated.")
                # Redirect to a success page or the profile page itself after successful update
                return redirect("your_profile")
        # Handle other submit types if needed
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, "customuser/your_profile.html", {"form": form})


def success(request):
    return render(request, "customuser/success.html")
