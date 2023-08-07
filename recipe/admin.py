from django import forms
from django.contrib import admin
from .models import Recipe
from recipeingredientintermediary.models import RecipeIngredientIntermediary


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ('recipe_ingredients',)


class RecipeIngredientIntermediaryInline(admin.TabularInline):
    model = RecipeIngredientIntermediary
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    inlines = [RecipeIngredientIntermediaryInline]


admin.site.register(Recipe, RecipeAdmin)