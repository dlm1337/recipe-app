from collections import OrderedDict
from django import forms  # import django forms
from recipeingredientintermediary.models import RecipeIngredientIntermediary
from .models import Recipe
from django.core.validators import MinValueValidator

SEARCH__CHOICES = (  # specify choices as a tuple
    (
        "#1",
        "Search by Your Recipes",
    ),
    ("#2", "Search by All Recipes"),
    ("#3", "Show All Recipes"),
)
AMOUNT_TYPES = (
    ("cup", "Cup"),
    ("teaspoon", "Teaspoon"),
    ("tablespoon", "Tablespoon"),
    ("fluid ounce", "Fluid Ounce"),
    ("pint", "Pint"),
    ("quart", "Quart"),
    ("gallon", "Gallon"),
    ("milliliter", "Milliliter"),
    ("liter", "Liter"),
    ("ounce", "Ounce"),
    ("pound", "Pound"),
    ("gram", "Gram"),
    ("kilogram", "Kilogram"),
    ("each", "Each"),
    ("other", "Other"),
)


class RecipeSearchForm(forms.Form):
    search_mode = forms.ChoiceField(choices=SEARCH__CHOICES)
    search = forms.CharField(max_length=150, required=False)


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = [
            "user",
            "recipe_ingredients",
        ]  # Exclude user and recipe_ingredient fields from the form

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance


class RecipeIngredientIntermediaryForm(forms.ModelForm):
    recipe_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    # Add the fields from RecipeIngredient
    ingredient = forms.CharField(max_length=255)
    calorie_content = forms.DecimalField(max_digits=8, decimal_places=2)
    amount = forms.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    amount_type = forms.ChoiceField(choices=AMOUNT_TYPES)
    cost = forms.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    supplier = forms.CharField(max_length=255)
    grams = forms.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta:
        model = RecipeIngredientIntermediary
        exclude = ["recipe", "recipe_ingredient"]  # Exclude the foreign key fields
