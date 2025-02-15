# CU Fitness

## Description
This project is to fulfill COEN 6311 requirements.

## Installation

### Prerequisites
- Python version required Python 3.11+

### Steps
```sh
# Clone the repository
git clone https://github.com/your-username/cu_fitness.git
cd cu_fitness

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Load initial data
python manage.py loaddata users
python manage.py loaddata goals
python manage.py loaddata workouts
```

## Usage
```sh
python manage.py runserver
```
