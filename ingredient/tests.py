from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Ingredient
# Create your tests here.

class IngredientModelTest(TestCase):
    def setUpTestData():
        # Set up non-modified objects used by all test methods
        Ingredient.objects.create(
            name="sugar",
        )

    def test_Ingredient_name(self): 
        ingredient = Ingredient.objects.get(id=1)
 
        field_label = ingredient._meta.get_field("name").verbose_name
 
        self.assertEqual(field_label, "name")

    def test_ingredient_name_not_null_or_blank(self):
        ingredient_blank = Ingredient(name="")
 
        with self.assertRaises(ValidationError):
            ingredient_blank.full_clean()
 

