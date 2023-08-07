from django.test import TestCase
from .models import RecipeIngredientIntermediary
from recipe.models import Recipe
from recipeingredient.models import RecipeIngredient
from ingredient.models import Ingredient
from customuser.models import CustomUser


# Create your tests here
class RecipeIngredientIntermediaryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create(
            username="fakeuser",
            email="fake@example.com",
            password="testpassword",
        )
        Recipe.objects.create(
            title="Nachos",
            directions="Put nachos on a plate with cheese, cook in microwave. Add sour cream, jalapenos, salsa, and lettuce.",
            cooking_time=50,
            star_count=5,
            recipe_type="snack",
            adapted_link="https://nachos.com",
            servings=3,
            yield_amount=12,
            allergens="unknown",
            user=cls.user,
        )
        ingredient = Ingredient.objects.create(name="cheese")
        curr_recipe = Recipe.objects.get(id=1)
        curr_recipeingredient = RecipeIngredient.objects.create(
            ingredient=ingredient,
            recipe=curr_recipe,
            calorie_content=20,
            amount=1.5,
            amount_type="cup",
            cost=20.40,
            supplier="supplier",
            grams=20.22,
        )
        RecipeIngredientIntermediary.objects.create(
            recipe=curr_recipe,
            recipe_ingredient=curr_recipeingredient,
        )

    def test_intermediary_recipe(self):
        intermediary = RecipeIngredientIntermediary.objects.get(id=1)

        field_label = intermediary._meta.get_field("recipe").verbose_name

        self.assertEqual(field_label, "recipe")

    def test_intermediary_recipeingredient(self):
        intermediary = RecipeIngredientIntermediary.objects.get(id=1)

        field_label = intermediary._meta.get_field("recipe_ingredient").verbose_name

        self.assertEqual(field_label, "recipe ingredient")
