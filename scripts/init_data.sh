#!/bin/bash

python manage.py loaddata users
python manage.py loaddata goals
python manage.py dumpdata workouts --indent 2 --output=workouts/fixtures/workouts_data.json
python manage.py loaddata meals
python manage.py loaddata ingredients
python manage.py loaddata meal_ingredients