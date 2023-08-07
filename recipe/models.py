from django.db import models
from django.shortcuts import reverse
from customuser.models import CustomUser 

RECIPE_TYPES = (
    ("breakfast", "Breakfast"),
    ("lunch", "Lunch"),
    ("dinner", "Dinner"),
    ("appetizer", "Appetizer"),
    ("dessert", "Dessert"),
    ("snack", "Snack"),
    ("drink", "Drink"),
    ("cocktail", "Cocktail"),
    ("other", "Other"),
)


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    recipe_ingredients = models.ManyToManyField(
        "recipeingredient.RecipeIngredient",
        through="recipeingredientintermediary.RecipeIngredientIntermediary",
    )
    directions = models.TextField()
    cooking_time = models.PositiveIntegerField(null=True, blank=False)
    star_count = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=False
    )
    recipe_type = models.CharField(max_length=100, choices=RECIPE_TYPES, blank=False)
    adapted_link = models.URLField(blank=True, null=True, default=None)
    servings = models.PositiveIntegerField(null=True, blank=False)
    yield_amount = models.IntegerField(blank=True, null=True, default=None)
    allergens = models.TextField(
        blank=True,
    )
    small_desc = models.TextField(
        max_length=200, default="No Description has been added currently."
    )
    pic = models.ImageField(upload_to="recipe", default="no_picture.jpg")

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse("recipe:detail", kwargs={"pk": self.pk})

    def calculate_difficulty(self):
        try:
            ingredients_len = len(self.recipe_ingredients.all())
            if self.cooking_time < 10 and ingredients_len < 4:
                return "Easy"
            elif self.cooking_time < 10 and ingredients_len > 4:
                return "Medium"
            elif self.cooking_time >= 10 and ingredients_len < 4:
                return "Intermediate"
            elif self.cooking_time >= 10 and ingredients_len >= 4:
                return "Hard"
        except:
            print("Missing an appropriate cooking time or ingredients.")
            return "Missing cooking time or ingredients."
