from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    calories_per_unit = models.FloatField(help_text="Calories per unit (e.g., per gram)")
    unit = models.CharField(max_length=50, default="g", help_text="Unit of measurement, e.g., g, ml, piece")

    # Macronutrients
    protein_per_unit = models.FloatField(default=0.0, help_text="Protein per unit (g)")

    carbohydrates_per_unit = models.FloatField(default=0.0, help_text="Total carbohydrates per unit (g)")
    fiber_per_unit = models.FloatField(default=0.0, help_text="Dietary fiber per unit (g)")
    sugars_per_unit = models.FloatField(default=0.0, help_text="Sugars per unit (g)")

    fat_per_unit = models.FloatField(default=0.0, help_text="Total fat per unit (g)")
    saturated_fat_per_unit = models.FloatField(default=0.0, help_text="Saturated fat per unit (g)")
    trans_fat_per_unit = models.FloatField(default=0.0, help_text="Trans fat per unit (g)")

    cholesterol_per_unit = models.FloatField(default=0.0, help_text="Cholesterol per unit (mg)")

    # Electrolytes (including zinc)
    sodium_per_unit = models.FloatField(default=0.0, help_text="Sodium per unit (mg)")
    potassium_per_unit = models.FloatField(default=0.0, help_text="Potassium per unit (mg)")
    calcium_per_unit = models.FloatField(default=0.0, help_text="Calcium per unit (mg)")
    zinc_per_unit = models.FloatField(default=0.0, help_text="Zinc per unit (mg)")

    # Vitamins
    vitamin_A_per_unit = models.FloatField(default=0.0, help_text="Vitamin A per unit (IU or mg)")
    vitamin_C_per_unit = models.FloatField(default=0.0, help_text="Vitamin C per unit (mg)")
    vitamin_B_per_unit = models.FloatField(default=0.0, help_text="Vitamin B per unit (mg)")
    vitamin_D_per_unit = models.FloatField(default=0.0, help_text="Vitamin D per unit (IU or μg)")

    def __str__(self):
        return self.name

class Meal(models.Model):
    meal_name = models.CharField(max_length=200)
    meal_type = models.CharField(max_length=50)  # e.g., Breakfast, Lunch, Dinner, Snack
    recipe_description = models.TextField()
    ingredients = models.TextField()  # Plain text listing (optional)
    cost = models.DecimalField(max_digits=6, decimal_places=2)  # e.g., 14.00
    cooking_duration = models.IntegerField()  # in minutes
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
        return sum(mi.get_calories() for mi in self.meal_ingredients.all())
    
    @property
    def total_protein(self):
        return sum(mi.get_protein() for mi in self.meal_ingredients.all())
    
    @property
    def total_carbohydrates(self):
        return sum(mi.get_carbohydrates() for mi in self.meal_ingredients.all())
    
    @property
    def total_fiber(self):
        return sum(mi.get_fiber() for mi in self.meal_ingredients.all())
    
    @property
    def total_sugars(self):
        return sum(mi.get_sugars() for mi in self.meal_ingredients.all())
    
    @property
    def total_fat(self):
        return sum(mi.get_fat() for mi in self.meal_ingredients.all())
    
    @property
    def total_saturated_fat(self):
        return sum(mi.get_saturated_fat() for mi in self.meal_ingredients.all())
    
    @property
    def total_trans_fat(self):
        return sum(mi.get_trans_fat() for mi in self.meal_ingredients.all())
    
    @property
    def total_cholesterol(self):
        return sum(mi.get_cholesterol() for mi in self.meal_ingredients.all())
    
    @property
    def total_sodium(self):
        return sum(mi.get_sodium() for mi in self.meal_ingredients.all())
    
    @property
    def total_potassium(self):
        return sum(mi.get_potassium() for mi in self.meal_ingredients.all())
    
    @property
    def total_calcium(self):
        return sum(mi.get_calcium() for mi in self.meal_ingredients.all())
    
    @property
    def total_zinc(self):
        return sum(mi.get_zinc() for mi in self.meal_ingredients.all())
    
    @property
    def total_vitamin_A(self):
        return sum(mi.get_vitamin_A() for mi in self.meal_ingredients.all())
    
    @property
    def total_vitamin_C(self):
        return sum(mi.get_vitamin_C() for mi in self.meal_ingredients.all())
    
    @property
    def total_vitamin_B(self):
        return sum(mi.get_vitamin_B() for mi in self.meal_ingredients.all())
    
    @property
    def total_vitamin_D(self):
        return sum(mi.get_vitamin_D() for mi in self.meal_ingredients.all())

class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="meal_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Quantity used in this meal (in the ingredient's unit)")

    def get_calories(self):
        return self.quantity * self.ingredient.calories_per_unit

    def get_protein(self):
        return self.quantity * self.ingredient.protein_per_unit

    def get_carbohydrates(self):
        return self.quantity * self.ingredient.carbohydrates_per_unit

    def get_fiber(self):
        return self.quantity * self.ingredient.fiber_per_unit

    def get_sugars(self):
        return self.quantity * self.ingredient.sugars_per_unit

    def get_fat(self):
        return self.quantity * self.ingredient.fat_per_unit

    def get_saturated_fat(self):
        return self.quantity * self.ingredient.saturated_fat_per_unit

    def get_trans_fat(self):
        return self.quantity * self.ingredient.trans_fat_per_unit

    def get_cholesterol(self):
        return self.quantity * self.ingredient.cholesterol_per_unit

    def get_sodium(self):
        return self.quantity * self.ingredient.sodium_per_unit

    def get_potassium(self):
        return self.quantity * self.ingredient.potassium_per_unit

    def get_calcium(self):
        return self.quantity * self.ingredient.calcium_per_unit

    def get_zinc(self):
        return self.quantity * self.ingredient.zinc_per_unit

    def get_vitamin_A(self):
        return self.quantity * self.ingredient.vitamin_A_per_unit

    def get_vitamin_C(self):
        return self.quantity * self.ingredient.vitamin_C_per_unit

    def get_vitamin_B(self):
        return self.quantity * self.ingredient.vitamin_B_per_unit

    def get_vitamin_D(self):
        return self.quantity * self.ingredient.vitamin_D_per_unit

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name} for {self.meal.meal_name}"

# -----------------------------
# NEW MODEL FOR DAILY INTAKES:
# -----------------------------
class RecommendedDailyIntake(models.Model):
    """
    Stores the recommended daily values for an 'average' adult.
    You can customize these fields/values as needed.
    """
    name = models.CharField(max_length=100, default="Average Adult")

    # Macros
    calories = models.FloatField(default=2000.0)    # e.g. 2000 kcal daily
    protein = models.FloatField(default=50.0)       # e.g. 50 g daily
    total_fat = models.FloatField(default=70.0)     # e.g. 70 g daily
    saturated_fat = models.FloatField(default=20.0)
    trans_fat = models.FloatField(default=2.0)
    carbohydrates = models.FloatField(default=260.0)
    fiber = models.FloatField(default=25.0)
    sugars = models.FloatField(default=50.0)
    cholesterol = models.FloatField(default=300.0)  # mg
    sodium = models.FloatField(default=2300.0)      # mg
    potassium = models.FloatField(default=3500.0)   # mg

    # Vitamins & Minerals
    vitamin_a = models.FloatField(default=900.0)    # IU or mcg (adjust as needed)
    vitamin_c = models.FloatField(default=90.0)     # mg
    vitamin_b = models.FloatField(default=1.3)      # mg (simplified for demonstration)
    vitamin_d = models.FloatField(default=600.0)    # IU (or 15 mcg)
    calcium = models.FloatField(default=1000.0)     # mg
    zinc = models.FloatField(default=11.0)          # mg

    def __str__(self):
        return self.name
