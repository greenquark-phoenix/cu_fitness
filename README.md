# CU Fitness

## Description
The purpose of this project is to develop an intelligent fitness application that helps users achieve their fitness 
goals through personalized guidance. The app integrates an AI assistant capable of providing tailored workout and meal 
recommendations based on user’s profile, fitness objectives, and dietary preferences and restrictions.

The goal is to create a user-friendly platform that empowers individuals to maintain a healthier lifestyle, while 
leveraging modern AI technologies to offer dynamic and context-aware suggestions. The application aims to simulate 
a real-life personal coach and nutritionist in a digital form, providing support through a chat-based interface.

This project is to fulfill COEN 6311 requirements.
## Installation

### Prerequisites
- Python version required Python 3.11+

### Steps
#### Clone the repository
```sh
git clone https://github.com/greenquark-phoenix/cu_fitness.git
cd cu_fitness
```

#### Create virtual environment
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

#### Install dependencies
```sh
pip install -r requirements.txt
```

## Setup
```sh
echo OPENAI_API_KEY=<add_your_key> > .env # Replace <add_your_key> with a valid key
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Load initial data
# Initially there are 5 users with usernames: belal, hamed, aurora, andy, and sudip. 
# The password is the username followed by 123.

./scripts/init_data.sh # On Windows use: .\scripts\init_data.bat
```

## Usage
```sh
python manage.py runserver
```
