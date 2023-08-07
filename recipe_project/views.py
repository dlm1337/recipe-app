from django.shortcuts import render, redirect

# Django authentication libraries
from django.contrib.auth import authenticate, login, logout

# Django Form for authentication
from django.contrib.auth.forms import AuthenticationForm


def login_view(request):
    error_message = None
    login_form = AuthenticationForm()  # Use a different context variable name

    if request.method == "POST":
        login_form = AuthenticationForm(data=request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/your_recipes")

        error_message = "ooops.. something went wrong"

    context = {
        "login_form": login_form,  # Use login_form context variable
        "error_message": error_message,
    }

    return render(request, "auth/login.html", context)


# define a function view called logout_view that takes a request from user
def logout_view(request):
    logout(request)  # the use pre-defined Django function to logout
    return redirect(
        "/success"
    )  # after logging out go to login form (or whichever page you want)
