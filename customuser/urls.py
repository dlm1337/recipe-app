from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns for your app...
    path("register/", views.register_user, name="register"),
    path("your_profile/", views.your_profile, name="your_profile"),
    path("success/", views.success, name="success"),
    # Other URL patterns
]
