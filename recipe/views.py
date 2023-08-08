import json
from django.views.generic import ListView, DetailView, FormView
from .models import Recipe
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RecipeForm, RecipeSearchForm, RecipeIngredientIntermediaryForm
import pandas as pd
from .utils import get_recipe_from_title, get_chart
from django.shortcuts import render
from django.utils.html import format_html
from .models import Recipe
from django.views.generic.edit import CreateView
from recipeingredient.models import RecipeIngredient
from ingredient.models import Ingredient
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import DeleteView


class RecipeHome(ListView):
    model = Recipe
    template_name = "recipe/recipes_home.html"

    def get_queryset(self):
        queryset = super().get_queryset()

        for recipe in queryset:
            recipe.title = get_recipe_from_title(recipe.title)

        return queryset


class YourRecipesView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "recipe/your_recipes.html"

    def get_queryset(self):
        ## function get_queryset is automatically called by ListView and get the request
        # user and filters recipes by username.
        user = self.request.user
        queryset = Recipe.objects.filter(user=user)

        return queryset


def format_cost(cost):
    return f"${cost:.2f}"


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipe/recipe_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Extract ingredient names from the RecipeIngredient objects
        try:
            ingredients = [
                ing.ingredient.name
                for ing in context["object"].recipe_ingredients.all()
            ]

            # Create a dictionary with ingredient names as keys
            ingredient_data = {ingredient: None for ingredient in ingredients}

            df = pd.DataFrame.from_dict(
                ingredient_data, orient="index", columns=["Calorie Content"]
            )

            # Set the 'Calorie Content', 'Grams' and 'Cost' for each ingredient
            for ing in context["object"].recipe_ingredients.all():
                df.loc[ing.ingredient.name, "Calorie Content"] = ing.calorie_content
                df.loc[ing.ingredient.name, "Grams"] = ing.grams
                df.loc[ing.ingredient.name, "Cost"] = format_cost(float(ing.cost))

            # Convert the DataFrame to HTML
            df_html = df.to_html(
                classes="table table-bordered table-hover", escape=False
            )

            # Manually add the table ID to the generated HTML
            df_html = df_html.replace("<table", '<table id="ingredient-info-table"')
            context["recipe_dataframe"] = df_html

            # Get the chart HTML using the get_chart
            chart1 = get_chart("#1", df, x=df.index, y="Calorie Content")
            chart2 = get_chart("#2", df, x=df.index, y="Grams")
            chart3 = get_chart("#3", df, x=df.index, y="Cost")

            context["chart1"] = chart1
            context["chart2"] = chart2
            context["chart3"] = chart3
        except Exception as e:
            print("No ingredients: ", str(e))

        return context


class RecipeSearchView(FormView):
    template_name = "recipe/search.html"
    form_class = RecipeSearchForm

    def form_valid(self, form):
        queryset = self.get_queryset(form)

        # Create a dictionary to store recipe titles and their absolute URLs
        recipe_urls = {recipe.title: recipe.get_absolute_url() for recipe in queryset}
        # Convert the recipe_urls dictionary to a JSON string
        recipe_urls_json = json.dumps(recipe_urls)

        # Convert the queryset to a DataFrame
        data = {
            "Recipe Title": [recipe.title for recipe in queryset],
            "Star Count": [recipe.star_count for recipe in queryset],
            "Cooking Time": [recipe.cooking_time for recipe in queryset],
            "Picture": [recipe.pic.url for recipe in queryset],
        }
        df = pd.DataFrame(data)

        # Modify the DataFrame to include the image as an HTML img tag
        df["Picture"] = df["Picture"].apply(
            lambda url: format_html('<img src="{}" width="200px">', url)
        )

        # Convert the modified DataFrame to HTML
        search_results_df = df.to_html(
            classes="table table-bordered table-hover", index=False, escape=False
        )
        # Manually add the table ID to the generated HTML
        search_results_df = search_results_df.replace(
            "<table", '<table id="search-results-table"'
        )

        context = {
            "search_results_df": search_results_df,
            "recipe_urls_json": recipe_urls_json,
        }

        return render(self.request, self.template_name, context)

    def get_queryset(self, form):
        search = form.cleaned_data.get("search")
        search_mode = form.cleaned_data.get("search_mode")

        if search_mode == "#1" and not self.request.user.is_authenticated:
            return Recipe.objects.none()

        queryset = Recipe.objects.all()

        if search_mode == "#1":
            # Filter recipes by the current user's recipes only
            queryset = Recipe.objects.filter(
                user=self.request.user, title__icontains=search
            )
            if search.strip():
                if not queryset.exists():
                    # Filter recipes by the ingredient name
                    queryset = Recipe.objects.filter(
                        user=self.request.user,
                        recipe_ingredients__ingredient__name__icontains=search,
                    )
            else:
                queryset = Recipe.objects.none()

        elif search_mode == "#2":
            # Only filter if the search bar is not blank
            if search.strip():
                queryset = Recipe.objects.filter(title__icontains=search)
                if not queryset.exists():
                    # Filter recipes by the ingredient name
                    queryset = Recipe.objects.filter(
                        recipe_ingredients__ingredient__name__icontains=search
                    )
            else:
                queryset = Recipe.objects.none()

        elif search_mode == "#3":
            queryset = Recipe.objects.all()

        return queryset


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipe/recipe_create.html"
    success_url = "/your_recipes"  # Use the actual URL name for success URL

    def form_valid(self, form):
        form.instance.user = (
            self.request.user
        )  # Set the logged-in user as the recipe creator
        return super().form_valid(form)


class IngredientAddView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeIngredientIntermediaryForm
    template_name = "recipe/add_ingredient.html"
    success_url = "/your_recipes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe_id = self.kwargs.get(
            "pk"
        )  # Assuming 'pk' is the keyword argument in your URL pattern
        context["form"].initial["recipe_id"] = recipe_id

        return context

    def form_valid(self, form):
        recipe_id = form.cleaned_data["recipe_id"]
        recipe = Recipe.objects.get(id=recipe_id)  # Get the Recipe object
        ingredient_name = form.cleaned_data["ingredient"]

        try:
            ingredient = Ingredient.objects.get(name=ingredient_name)
        except Ingredient.DoesNotExist:
            ingredient = Ingredient(name=ingredient_name)
            ingredient.save()

        recipe_ingredient = RecipeIngredient()
        recipe_ingredient.ingredient = ingredient
        recipe_ingredient.calorie_content = form.cleaned_data["calorie_content"]
        recipe_ingredient.amount = form.cleaned_data["amount"]
        recipe_ingredient.amount_type = form.cleaned_data["amount_type"]
        recipe_ingredient.cost = form.cleaned_data["cost"]
        recipe_ingredient.supplier = form.cleaned_data["supplier"]
        recipe_ingredient.grams = form.cleaned_data["grams"]
        recipe_ingredient.save()

        recipe_ingredient_intermediary = form.save(commit=False)
        recipe_ingredient_intermediary.recipe = recipe
        recipe_ingredient_intermediary.recipe_ingredient = recipe_ingredient
        recipe_ingredient_intermediary.save()

        return super().form_valid(form)


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = "recipe/delete.html"
    success_url = reverse_lazy("recipe:your_recipes")
