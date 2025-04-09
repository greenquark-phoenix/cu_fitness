#!/bin/bash

python manage.py loaddata users
python manage.py loaddata goals
python manage.py loaddata workouts
python manage.py loaddata meals