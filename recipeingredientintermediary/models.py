from django.db import models


class RecipeIngredientIntermediary(models.Model):
    recipe = models.ForeignKey("recipe.Recipe", on_delete=models.CASCADE)
    recipe_ingredient = models.ForeignKey(
        "recipeingredient.RecipeIngredient", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.recipe.title} - {self.recipe_ingredient.ingredient.name}"
