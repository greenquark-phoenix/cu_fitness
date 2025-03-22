from django.db import models
from django.contrib.auth.models import User

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

    dv_calories = models.FloatField(default=0.0)
    dv_protein = models.FloatField(default=0.0)
    dv_fat = models.FloatField(default=0.0)
    dv_saturated_fat = models.FloatField(default=0.0)
    dv_trans_fat = models.FloatField(default=0.0)
    dv_cholesterol = models.FloatField(default=0.0)
    dv_sodium = models.FloatField(default=0.0)
    dv_potassium = models.FloatField(default=0.0)
    dv_carbohydrates = models.FloatField(default=0.0)
    dv_fiber = models.FloatField(default=0.0)
    dv_sugars = models.FloatField(default=0.0)
    dv_vitamin_A = models.FloatField(default=0.0)
    dv_vitamin_C = models.FloatField(default=0.0)
    dv_vitamin_B = models.FloatField(default=0.0)
    dv_vitamin_D = models.FloatField(default=0.0)
    dv_calcium = models.FloatField(default=0.0)
    dv_zinc = models.FloatField(default=0.0)

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

    def update_dv_fields(self):
        from .models import RecommendedDailyIntake
        rdi = RecommendedDailyIntake.objects.first()
        if not rdi:
            return

        total_cals = self.total_calories
        if rdi.calories:
            self.dv_calories = (total_cals / rdi.calories) * 100
        else:
            self.dv_calories = 0

        total_pro = self.total_protein
        if rdi.protein:
            self.dv_protein = (total_pro / rdi.protein) * 100
        else:
            self.dv_protein = 0

        total_fat = self.total_fat
        if rdi.total_fat:
            self.dv_fat = (total_fat / rdi.total_fat) * 100
        else:
            self.dv_fat = 0

        sat_fat = self.total_saturated_fat
        if rdi.saturated_fat:
            self.dv_saturated_fat = (sat_fat / rdi.saturated_fat) * 100
        else:
            self.dv_saturated_fat = 0

        trans_fat = self.total_trans_fat
        if rdi.trans_fat:
            self.dv_trans_fat = (trans_fat / rdi.trans_fat) * 100
        else:
            self.dv_trans_fat = 0

        chol = self.total_cholesterol
        if rdi.cholesterol:
            self.dv_cholesterol = (chol / rdi.cholesterol) * 100
        else:
            self.dv_cholesterol = 0

        sod = self.total_sodium
        if rdi.sodium:
            self.dv_sodium = (sod / rdi.sodium) * 100
        else:
            self.dv_sodium = 0

        pot = self.total_potassium
        if rdi.potassium:
            self.dv_potassium = (pot / rdi.potassium) * 100
        else:
            self.dv_potassium = 0

        carbs = self.total_carbohydrates
        if rdi.carbohydrates:
            self.dv_carbohydrates = (carbs / rdi.carbohydrates) * 100
        else:
            self.dv_carbohydrates = 0

        fib = self.total_fiber
        if rdi.fiber:
            self.dv_fiber = (fib / rdi.fiber) * 100
        else:
            self.dv_fiber = 0

        sug = self.total_sugars
        if rdi.sugars:
            self.dv_sugars = (sug / rdi.sugars) * 100
        else:
            self.dv_sugars = 0

        vitA = self.total_vitamin_A
        if rdi.vitamin_a:
            self.dv_vitamin_A = (vitA / rdi.vitamin_a) * 100
        else:
            self.dv_vitamin_A = 0

        vitC = self.total_vitamin_C
        if rdi.vitamin_c:
            self.dv_vitamin_C = (vitC / rdi.vitamin_c) * 100
        else:
            self.dv_vitamin_C = 0

        vitB = self.total_vitamin_B
        if rdi.vitamin_b:
            self.dv_vitamin_B = (vitB / rdi.vitamin_b) * 100
        else:
            self.dv_vitamin_B = 0

        vitD = self.total_vitamin_D
        if rdi.vitamin_d:
            self.dv_vitamin_D = (vitD / rdi.vitamin_d) * 100
        else:
            self.dv_vitamin_D = 0

        calc = self.total_calcium
        if rdi.calcium:
            self.dv_calcium = (calc / rdi.calcium) * 100
        else:
            self.dv_calcium = 0

        zn = self.total_zinc
        if rdi.zinc:
            self.dv_zinc = (zn / rdi.zinc) * 100
        else:
            self.dv_zinc = 0

        self.save()


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


class RecommendedDailyIntake(models.Model):
    name = models.CharField(max_length=100, default="Average Adult")
    calories = models.FloatField(default=2000.0)
    protein = models.FloatField(default=50.0)
    total_fat = models.FloatField(default=70.0)
    saturated_fat = models.FloatField(default=20.0)
    trans_fat = models.FloatField(default=2.0)
    carbohydrates = models.FloatField(default=260.0)
    fiber = models.FloatField(default=25.0)
    sugars = models.FloatField(default=50.0)
    cholesterol = models.FloatField(default=300.0)
    sodium = models.FloatField(default=2300.0)
    potassium = models.FloatField(default=3500.0)
    vitamin_a = models.FloatField(default=900.0)
    vitamin_c = models.FloatField(default=90.0)
    vitamin_b = models.FloatField(default=1.3)
    vitamin_d = models.FloatField(default=600.0)
    calcium = models.FloatField(default=1000.0)
    zinc = models.FloatField(default=11.0)

    def __str__(self):
        return self.name


# Model to store each user's meal selection status
class UserMealSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    selected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'meal')

    def __str__(self):
        return f"{self.user.username} - {self.meal.meal_name} - selected={self.selected}"
