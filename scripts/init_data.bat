@echo off

python manage.py loaddata users
python manage.py loaddata goals
python manage.py loaddata workouts
python manage.py loaddata meals
python manage.py loaddata schedule
python manage.py loaddata mylist