import json
import os
import uuid
from django.test import TestCase, override_settings, Client
from .models import Recipe
from django.core.exceptions import ValidationError
from recipeingredient.models import RecipeIngredient
from ingredient.models import Ingredient
from recipeingredientintermediary.models import RecipeIngredientIntermediary
from django.core.files import File
from customuser.models import CustomUser
from .forms import RecipeSearchForm, RecipeForm, RecipeIngredientIntermediaryForm
from django.urls import reverse
from .utils import get_recipe_from_title
from unittest.mock import patch
from pandas import DataFrame
from recipe.views import format_cost
from django.contrib.auth import get_user_model
import pandas as pd


# Create your tests here.


class RecipeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a fake user
        cls.user = CustomUser.objects.create(
            username="fakeuser",
            email="fake@example.com",
            password="testpassword",
        )

        # Create Recipe objects and associate them with the fake user
        Recipe.objects.create(
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
        Recipe.objects.create(
            title="Pancakes",
            directions="Mix ingredients, cook on a griddle, serve with syrup.",
            cooking_time=9,
            star_count=4,
            recipe_type="breakfast",
            servings=2,
            user=cls.user,
        )
        recipe = Recipe.objects.create(
            title="Test Recipe",
            directions="Test Directions",
            cooking_time=15,
            star_count=4,
            recipe_type="snack",
            servings=1,
            user=cls.user,
        )

        ri1 = RecipeIngredient.objects.create(
            ingredient=Ingredient.objects.create(name="Ingredient 1"),
            calorie_content=20,
            amount=1.5,
            amount_type="cup",
            cost=20.40,
            supplier="supplier",
            grams=20.22,
        )

        ri2 = RecipeIngredient.objects.create(
            ingredient=Ingredient.objects.create(name="Ingredient 2"),
            calorie_content=10,
            amount=0.5,
            amount_type="teaspoon",
            cost=5.10,
            supplier="supplier",
            grams=5.25,
        )

        ri3 = RecipeIngredient.objects.create(
            ingredient=Ingredient.objects.create(name="Ingredient 3"),
            calorie_content=30,
            amount=2,
            amount_type="tablespoon",
            cost=10.15,
            supplier="supplier",
            grams=25.50,
        )

        ri4 = RecipeIngredient.objects.create(
            ingredient=Ingredient.objects.create(name="Ingredient 4"),
            calorie_content=30,
            amount=2,
            amount_type="tablespoon",
            cost=10.15,
            supplier="supplier",
            grams=25.50,
        )

        # Retrieve the Recipe instance and associate RecipeIngredients with it
        recipe = Recipe.objects.get(id=1)
        recipe.recipe_ingredients.add(ri1)

        recipe2 = Recipe.objects.get(id=2)
        recipe2.recipe_ingredients.add(ri1, ri2, ri3, ri4)

    def test_recipe_title(self):
        recipe = Recipe.objects.get(id=1)

        field_label = recipe._meta.get_field("title").verbose_name

        self.assertEqual(field_label, "title")

    def test_recipe_directions(self):
        recipe = Recipe.objects.get(id=1)
        expected_directions = "Put nachos on a plate with cheese, cook in microwave. Add sour cream, jalapenos, salsa, and lettuce."
        self.assertEqual(recipe.directions, expected_directions)

    def test_recipe_cooking_time(self):
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.cooking_time, 3)

    def test_recipe_star_count(self):
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.star_count, 5)

    def test_recipe_recipe_type(self):
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.recipe_type, "snack")

    def test_recipe_adapted_link(self):
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.adapted_link, "https://nachos.com")

    def test_recipe_servings(self):
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.servings, 3)

    def test_recipe_yield_amount(self):
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.yield_amount, 12)

    def test_recipe_allergens(self):
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.allergens, "unknown")

    def test_recipe_id_auto_increment(self):
        recipe1 = Recipe.objects.get(id=2)
        recipe2 = Recipe.objects.get(id=3)
        self.assertEqual(recipe1.id, 2)
        self.assertEqual(recipe2.id, 3)

    def test_recipe_cooking_time_not_negative(self):
        recipe = Recipe(cooking_time=-10)
        with self.assertRaises(ValidationError):
            recipe.clean_fields(exclude=["id"])

    def test_recipe_star_count_not_negative(self):
        recipe = Recipe(star_count=-2)
        with self.assertRaises(ValidationError):
            recipe.clean_fields(exclude=["id"])

    def test_recipe_servings_not_negative(self):
        recipe = Recipe(servings=-3)
        with self.assertRaises(ValidationError):
            recipe.clean_fields(exclude=["id"])

    def test_recipe_yield_amount_not_negative(self):
        recipe = Recipe(yield_amount=-1)
        with self.assertRaises(ValidationError):
            recipe.clean_fields(exclude=["id"])

    def test_get_absolute_url(self):
        # testing details page link.
        recipe = Recipe.objects.get(id=1)
        self.assertEqual(recipe.get_absolute_url(), "/detail/1")

    def test_home_page_link(self):
        # testing home page.
        client = Client()
        response = client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_calculate_difficulty_easy(self):
        # Create RecipeIngredientIntermediary instances to associate RecipeIngredients with the Recipe
        RecipeIngredientIntermediary.objects.create(
            recipe=Recipe.objects.get(id=1),
            recipe_ingredient=RecipeIngredient.objects.get(id=1),
        )

        recipe = Recipe.objects.get(id=1)

        result = recipe.calculate_difficulty()

        self.assertEqual(result, "Easy")

    def test_calculate_difficulty_medium(self):
        recipe = Recipe.objects.get(id=2)
        RecipeIngredientIntermediary.objects.create(
            recipe=Recipe.objects.get(id=2),
            recipe_ingredient=RecipeIngredient.objects.get(id=1),
        )
        RecipeIngredientIntermediary.objects.create(
            recipe=Recipe.objects.get(id=2),
            recipe_ingredient=RecipeIngredient.objects.get(id=2),
        )
        RecipeIngredientIntermediary.objects.create(
            recipe=Recipe.objects.get(id=2),
            recipe_ingredient=RecipeIngredient.objects.get(id=3),
        )
        RecipeIngredientIntermediary.objects.create(
            recipe=Recipe.objects.get(id=2),
            recipe_ingredient=RecipeIngredient.objects.get(id=4),
        )
        result = recipe.calculate_difficulty()

        self.assertEqual(result, "Medium")

    def test_calculate_difficulty_missing_data(self):
        # Test for missing cooking time or ingredients
        # The method should return "Missing cooking time or ingredients." when forced into
        # exception
        recipe = Recipe()
        result = recipe.calculate_difficulty()
        self.assertEqual(result, "Missing cooking time or ingredients.")

    @override_settings(
        MEDIA_ROOT="/tmp"
    )  # Override the MEDIA_ROOT setting to use a temporary directory
    def test_recipe_pic(self):
        # Use the existing "no_picture.jpg" from the media folder
        image_path = os.path.join("media", "no_picture.jpg")

        # Assert that the file exists in the media folder
        self.assertTrue(os.path.exists(image_path))

        # Generate a unique identifier for the test image file name
        test_image_name = f"test_no_picture_{uuid.uuid4().hex}.jpg"

        # Create a Recipe instance without setting the pic attribute
        recipe = Recipe.objects.get(id=3)
        # Set the pic attribute using the existing "no_picture.jpg" file
        with open(image_path, "rb") as f:
            recipe.pic.save(test_image_name, File(f))

        # Retrieve the Recipe instance and check if the pic attribute is set correctly
        recipe = Recipe.objects.get(id=recipe.id)
        expected_pic_path = os.path.join("recipe", test_image_name)

        # Replace backslashes with forward slashes in the expected path to make it platform-independent
        expected_pic_path = expected_pic_path.replace("\\", "/")

        self.assertEqual(recipe.pic.name, expected_pic_path)


class RecipeFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.form_data_valid = {
            "search_mode": "#1",
            "search": "Recipe Name",
        }
        cls.form_data_invalid = {
            "search_mode": "#4",  # An invalid choice
            "search": "Recipe Name",
        }
        cls.form_data_blank_search_mode = {
            "search_mode": "",  # An empty choice
            "search": "Recipe Name",
        }
        cls.form_data_blank_ingredient = {
            "search_mode": "#3",
            "search": "",  # Blank input for "#3" search mode
        }

    def test_valid_search_mode(self):
        form = RecipeSearchForm(data=self.form_data_valid)
        # verify the form fields values and check for validation errors
        self.assertTrue(
            form.is_valid(), "Form should be valid with a valid search mode"
        )
        self.assertEqual(form.cleaned_data["search_mode"], "#1")
        self.assertEqual(form.cleaned_data["search"], "Recipe Name")

    def test_invalid_search_mode(self):
        form = RecipeSearchForm(data=self.form_data_invalid)
        # verify the form fields values and check for validation errors
        self.assertFalse(form.is_valid())
        self.assertIn("search_mode", form.errors)

    def test_blank_search_mode(self):
        form = RecipeSearchForm(data=self.form_data_blank_search_mode)
        # verify the form fields values and check for validation errors
        self.assertFalse(form.is_valid())
        self.assertIn("search_mode", form.errors)

    def test_blank_search(self):
        form = RecipeSearchForm(data=self.form_data_blank_ingredient)
        # verify the form fields values and check for validation errors
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["search_mode"], "#3")
        self.assertEqual(form.cleaned_data["search"], "")


class RecipeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        cls.recipe = Recipe.objects.create(
            title="Nachos",
            directions="Put nachos on a plate with cheese, cook in microwave. Add sour cream, jalapenos, salsa, and lettuce.",
            cooking_time=3,
            star_count=5,
            recipe_type="snack",
            adapted_link="https://nachos.com",
            servings=3,
            yield_amount=12,
            allergens="unknown",
            user=cls.user,  # Associate the user with the recipe
            pic="no_picture.jpg",
        )
        RecipeIngredient.objects.create(
            recipe=cls.recipe,
            ingredient=Ingredient.objects.create(name="Ingredient 1"),
            calorie_content=20,
            amount=1.5,
            amount_type="cup",
            cost=20.40,
            supplier="supplier",
            grams=20.22,
        )

        RecipeIngredient.objects.create(
            recipe=cls.recipe,
            ingredient=Ingredient.objects.create(name="Ingredient 2"),
            calorie_content=10,
            amount=0.5,
            amount_type="teaspoon",
            cost=5.10,
            supplier="supplier",
            grams=5.25,
        )

        RecipeIngredient.objects.create(
            recipe=cls.recipe,
            ingredient=Ingredient.objects.create(name="Ingredient 3"),
            calorie_content=30,
            amount=2,
            amount_type="tablespoon",
            cost=10.15,
            supplier="supplier",
            grams=25.50,
        )

        cls.recipe = Recipe.objects.get(id=1)

    def test_recipe_home_view(self):
        response = self.client.get(reverse("recipe:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipe/recipes_home.html")
        self.assertContains(response, "Nachos")

    def test_recipe_home_view_with_custom_title(self):
        # Modify the recipe title with the custom function
        self.recipe.title = get_recipe_from_title(self.recipe.title)

        response = self.client.get(reverse("recipe:home"))
        self.assertContains(response, self.recipe.title)

    def test_recipe_list_view_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("recipe:your_recipes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nachos")

    def test_recipe_list_view_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse("recipe:your_recipes"))
        self.assertEqual(response.status_code, 302)
        # Redirects to the login page as expected for an anonymous user

    @staticmethod
    def mock_get_chart(*args, **kwargs):
        return "<div>Mocked Chart</div>"

    def test_recipe_detail_view(self):
        # ... Existing test setup ...

        # Mock DataFrame data
        data = {
            "Ingredient": ["Ingredient 1", "Ingredient 2", "Ingredient 3"],
            "Calorie Content": [20, 10, 30],
            "Grams": [20.22, 5.25, 25.50],
            "Cost": ["$20.40", "$5.10", "$10.15"],
        }

        # Convert the data into a DataFrame
        mock_df = DataFrame(data)

        # Set the DataFrame as the mocked DataFrame to be returned by the mock function
        with patch("recipe.views.get_chart", side_effect=self.mock_get_chart), patch(
            "recipe.views.pd.DataFrame.from_dict", return_value=mock_df
        ):
            url = reverse("recipe:detail", kwargs={"pk": self.recipe.pk})
            response = self.client.get(url)

            # Check if the view returns a 200 status code
            self.assertEqual(response.status_code, 200)

            # Check if the recipe title is present in the response
            self.assertContains(response, self.recipe.title)

            # Check if the ingredient names are present in the response
            for ing in self.recipe.recipe_ingredients.all():
                self.assertContains(response, ing.ingredient.name)

            # Check if the calorie content, grams, and cost are present in the response
            for ing in self.recipe.recipe_ingredients.all():
                self.assertContains(response, str(ing.calorie_content))
                self.assertContains(
                    response, str(round(ing.grams, 2))
                )  # Use round function
                self.assertContains(response, format_cost(float(ing.cost)))

            # Check if the DataFrame data is present in the response
            for col in data.keys():
                for value in data[col]:
                    self.assertContains(response, str(value))  # Convert value to string

            # Check if the charts are present in the response
            self.assertContains(response, "<div>Mocked Chart</div>")

    @patch("recipe.views.RecipeSearchView.get_queryset")
    @patch("recipe.views.pd.DataFrame.from_dict")
    def test_recipe_search_view(self, mock_from_dict, mock_get_queryset):
        # Mock the queryset returned by get_queryset method
        mock_get_queryset.return_value = [self.recipe]

        # Mock the DataFrame returned by pd.DataFrame.from_dict
        df_data = {
            "Recipe Title": [self.recipe.title],
            "Star Count": [self.recipe.star_count],
            "Cooking Time": [self.recipe.cooking_time],
            "Picture": [self.recipe.pic.url],
        }
        mock_df = pd.DataFrame(df_data)
        mock_df["Picture"] = mock_df["Picture"].apply(
            lambda url: f'<img src="{url}" width="200px">'
        )
        mock_from_dict.return_value = mock_df

        url = reverse("recipe:search")
        search_data = {"search": "Nachos", "search_mode": "#2"}
        response = self.client.post(url, search_data)

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, "recipe/search.html")

        # Check that the form used in the view is the correct form
        self.assertIsInstance(response.context["form"], RecipeSearchForm)

        # Check that the recipe data is present in the response
        self.assertContains(response, "Nachos")

        # Check that the JSON data for recipe URLs is present in the response
        self.assertIn("recipe_urls_json", response.context)
        recipe_urls_json = response.context["recipe_urls_json"]
        recipe_urls_dict = json.loads(recipe_urls_json)
        self.assertEqual(
            recipe_urls_dict[self.recipe.title], self.recipe.get_absolute_url()
        )

        # Check that the DataFrame HTML is present in the response
        self.assertIn("search_results_df", response.context)
        search_results_df = response.context["search_results_df"]
        expected_table = mock_df.to_html(
            classes="table table-bordered table-hover", index=False, escape=False
        )

        # Check if each cell of the expected table is present in the response
        for cell in expected_table.split():
            if cell.startswith("<img"):  # Ignore the img tag modification
                continue
            self.assertContains(response, cell.strip())


class RecipeCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_recipe_create_view_get(self):
        response = self.client.get(reverse("recipe:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipe/recipe_create.html")
        self.assertIsInstance(response.context["form"], RecipeForm)

    def test_recipe_create_view_post_valid(self):
        data = {
            "title": "Test Recipe",
            "directions": "afraefegseg",
            "cooking_time": 30,
            "star_count": 4,
            "recipe_type": "breakfast",
            "adapted_link": "https://example.com",
            "servings": 4,
            "yield_amount": 6,
            "allergens": "Dairy, Nuts",
            "small_desc": "Test description",
            "pic": "no_picture.jpg",
            "user": self.user,
        }
        response = self.client.post(reverse("recipe:create"), data)
        self.assertEqual(response.status_code, 302)

    def test_recipe_create_view_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("recipe:create"))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(response, "/login/?next=/create/")


class IngredientAddViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )

        # Create a test recipe
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            directions="afraefegseg",
            cooking_time=30,
            star_count=4,
            recipe_type="breakfast",
            adapted_link="https://example.com",
            servings=4,
            yield_amount=6,
            allergens="Dairy, Nuts",
            small_desc="Test description",
            pic="no_picture.jpg",
            user=self.user,
        )
        # URL for the IngredientAddView
        self.url = reverse("recipe:add_ingredient", kwargs={"pk": self.recipe.id})

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipe/add_ingredient.html")

    def test_view_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code, 302
        )  # 302 is the redirect status code for unauthorized access
        self.assertRedirects(response, "/login/?next=/add_ingredient/1/")

    def test_form_submission(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            self.url,
            {
                "ingredient": Ingredient.objects.create(name="Ingredient 2"),
                "calorie_content": 100,
                "amount": 2,
                "amount_type": "oz",
                "cost": 5.0,
                "supplier": "Test Supplier",
                "grams": 50,
            },
        )

        self.assertEqual(response.status_code, 200)


class RecipeFormTests(TestCase):
    def test_form_save(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        form_data = {
            "title": "Test Recipe",
            "directions": "afraefegseg",
            "cooking_time": 30,
            "star_count": 4,
            "recipe_type": "breakfast",
            "adapted_link": "https://example.com",
            "servings": 4,
            "yield_amount": 6,
            "allergens": "Dairy, Nuts",
            "small_desc": "Test description",
            "pic": "no_picture.jpg",
        }

        # Create an instance of the form with the form data
        form = RecipeForm(data=form_data)
        form.instance.user = self.user
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data

        recipe = form.save()

        # Check if the recipe was saved correctly
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.title, cleaned_data["title"])
        self.assertEqual(recipe.cooking_time, cleaned_data["cooking_time"])
        self.assertEqual(recipe.star_count, cleaned_data["star_count"])
        self.assertEqual(recipe.recipe_type, cleaned_data["recipe_type"])
        self.assertEqual(recipe.adapted_link, cleaned_data["adapted_link"])
        self.assertEqual(recipe.servings, cleaned_data["servings"])
        self.assertEqual(recipe.yield_amount, cleaned_data["yield_amount"])
        self.assertEqual(recipe.allergens, cleaned_data["allergens"])
        self.assertEqual(recipe.small_desc, cleaned_data["small_desc"])


class RecipeIngredientIntermediaryFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            "ingredient": {"name": "ingredient"},
            "calorie_content": 50,  # Invalid calorie content
            "amount": 100,  # Invalid negative amount
            "amount_type": "cup",  # Invalid amount type
            "cost": 0,  # Invalid cost (minimum value is 0)
            "supplier": "awdawd",  # Invalid empty supplier
            "grams": 150,
        }
        form = RecipeIngredientIntermediaryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            "ingredient": "Flour",
            "calorie_content": 100,
            "amount": 250,
            "amount_type": "grams",
            "cost": 2.5,
            "supplier": "wadawd",
            "grams": 250,
        }
        form = RecipeIngredientIntermediaryForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  # Expecting 4 fields with errors

    def test_missing_required_fields(self):
        form_data = {
            # Missing required fields ingredient, amount, amount_type, cost, supplier
            "calorie_content": 150,
            "grams": 200,
        }
        form = RecipeIngredientIntermediaryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)  # Expecting 5 missing field errors


class RecipeDeleteViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            directions="afraefegseg",
            cooking_time=30,
            star_count=4,
            recipe_type="breakfast",
            adapted_link="https://example.com",
            servings=4,
            yield_amount=6,
            allergens="Dairy, Nuts",
            small_desc="Test description",
            pic="no_picture.jpg",
            user=self.user,
        )
        self.url = reverse("recipe:delete", args=[self.recipe.pk])

    def test_view_accessible_by_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipe/delete.html")

    def test_view_inaccessible_by_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_deletion(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # Redirects after deletion
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())
