# CU Fitness

## Description
This project is to fulfill COEN 6311 requirements.

## Installation

### Prerequisites
- Python version required Python 3.11+

### Steps
```sh
# Clone the repository
git clone https://github.com/greenquark-phoenix/cu_fitness.git
cd cu_fitness

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup
echo OPENAI_API_KEY=<add_your_key> > .env # Replace <add_your_key> with a valid key
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Load initial data
# Initially there are 5 users with usernames: belal, hamed, aurora, andy, sudip. The password is the username followed by 123.

./scripts/init_data.sh # On Windows use: .\scripts\init_data.bat

## Usage
```sh
python manage.py runserver
```
