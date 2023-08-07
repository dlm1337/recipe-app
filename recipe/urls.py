from django.urls import path
from .views import YourRecipesView
from .views import RecipeDetailView
from .views import RecipeHome
from .views import RecipeSearchView
from .views import RecipeCreateView, IngredientAddView, RecipeDeleteView

app_name = "recipe"


urlpatterns = [
    path("", RecipeHome.as_view(), name="home"),
    path("your_recipes/", YourRecipesView.as_view(), name="your_recipes"),
    path("detail/<pk>", RecipeDetailView.as_view(), name="detail"),
    path("search/", RecipeSearchView.as_view(), name="search"),
    path("create/", RecipeCreateView.as_view(), name="create"),
    path(
        "add_ingredient/<int:pk>/", IngredientAddView.as_view(), name="add_ingredient"
    ),
    path("delete/<int:pk>/", RecipeDeleteView.as_view(), name="delete"),
]
