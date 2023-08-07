from django.db import models
from django.core.validators import MinValueValidator

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


class RecipeIngredient(models.Model):
    id = models.AutoField(primary_key=True)
    ingredient = models.ForeignKey("ingredient.Ingredient", on_delete=models.CASCADE)
    calorie_content = models.DecimalField(max_digits=8, decimal_places=2)
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    amount_type = models.CharField(max_length=100, choices=AMOUNT_TYPES)
    cost = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    supplier = models.CharField(max_length=255)
    grams = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"Recipe Ingredient: {self.id} - {self.ingredient.name}"
