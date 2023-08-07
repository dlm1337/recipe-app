from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import RecipeIngredient
from ingredient.models import Ingredient
from recipe.models import Recipe
from customuser.models import CustomUser


# Create your tests here
class RecipeIngredientModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a fake user
        cls.user = CustomUser.objects.create(
            username="fakeuser",
            email="fake@example.com",
            password="testpassword",
        )

        ingredient = Ingredient.objects.create(name="Ingredient 1")
        recipe = Recipe.objects.create(
            title="Nachos",
            directions="Put nachos on a plate with cheese, cook in microwave. Add sour cream, jalapenos, salsa, and lettuce.",
            cooking_time=3,
            star_count=5,
            recipe_type="snack",
            adapted_link="https://nachos.com",
            servings=3,
            yield_amount=12,
            allergens="unknown",
            user=cls.user,
        )

        RecipeIngredient.objects.create(
            ingredient=ingredient,
            recipe=recipe,
            calorie_content=20,
            amount=1.5,
            amount_type="cup",
            cost=20.40,
            supplier="supplier",
            grams=20.22,
        )

    def test_recipeingredient_supplier(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)

        field_label = recipe_ingredient._meta.get_field("supplier").verbose_name

        self.assertEqual(field_label, "supplier")

    def test_ingredient_name(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_ingredient_name = "Ingredient 1"
        self.assertEqual(recipe_ingredient.ingredient.name, expected_ingredient_name)

    def test_recipe_title(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_recipe_title = recipe_ingredient.ingredient
        self.assertEqual(recipe_ingredient.ingredient, expected_recipe_title)

    def test_calorie_content(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_calorie_content = 20
        self.assertEqual(recipe_ingredient.calorie_content, expected_calorie_content)

    def test_amount(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_amount = 1.5
        self.assertEqual(recipe_ingredient.amount, expected_amount)

    def test_amount_type(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_amount_type = "cup"
        self.assertEqual(recipe_ingredient.amount_type, expected_amount_type)

    def test_supplier(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_supplier = "supplier"
        self.assertEqual(recipe_ingredient.supplier, expected_supplier)

    def test_cost(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_cost = Decimal("20.40")
        self.assertEqual(recipe_ingredient.cost, expected_cost)

    def test_grams(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_grams = Decimal("20.22")
        self.assertEqual(recipe_ingredient.grams, expected_grams)

    def test_invalid_cost(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        recipe_ingredient.cost = -10.50
        with self.assertRaises(ValidationError):
            recipe_ingredient.full_clean()

    def test_invalid_grams(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        recipe_ingredient.grams = Decimal("-10.75")
        with self.assertRaises(ValidationError):
            recipe_ingredient.full_clean()

    def test_blank_supplier(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        recipe_ingredient.supplier = ""
        with self.assertRaises(ValidationError):
            recipe_ingredient.full_clean()
