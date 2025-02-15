from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    calories_per_unit = models.FloatField(help_text="Calories per unit (e.g., per gram)")
    unit = models.CharField(max_length=50, default="g", help_text="Unit of measurement, e.g., g, ml, piece")

    def __str__(self):
        return self.name

class Meal(models.Model):
    meal_name = models.CharField(max_length=200)
    meal_type = models.CharField(max_length=50)  # e.g., Breakfast, Lunch, Dinner, Snack
    recipe_description = models.TextField()
    ingredients = models.TextField()  # For plain text listing (optional, if you want to display unstructured ingredients)
    cost = models.DecimalField(max_digits=6, decimal_places=2)  # e.g., 14.00
    cooking_duration = models.IntegerField()  # in minutes, renamed from duration
    image = models.ImageField(upload_to='meals/', blank=True, null=True)  # Requires Pillow
    cooking_instructions = models.TextField(default="Cooking instructions not provided yet.")

    DIET_CHOICES = [
        ('non-veg', 'Non-Vegetarian'),
        ('veg', 'Vegetarian'),
        ('vegan', 'Vegan'),
    ]
    diet_type = models.CharField(max_length=10, choices=DIET_CHOICES, default='non-veg')

    def __str__(self):
        return self.meal_name

    @property
    def total_calories(self):
        # Sum up calories from all associated MealIngredient entries.
        return sum(mi.get_calories() for mi in self.meal_ingredients.all())

class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="meal_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Quantity used in this meal (in the ingredient's unit)")

    def get_calories(self):
        # Calculate total calories contributed by this ingredient.
        return self.quantity * self.ingredient.calories_per_unit

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name} for {self.meal.meal_name}"
