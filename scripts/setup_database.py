"""
Database setup script
Run this after starting the containers to set up the database
"""
import os
import sys
import django

# Add the project directory
sys.path.append('/app')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_api.settings')
django.setup()

from django.core.management import execute_from_command_line

def setup_database():
    """Setup database with migrations and create superuser"""
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("Creating superuser...")
    execute_from_command_line(['manage.py', 'createsuperuser', '--noinput', '--username', 'admin', '--email', 'admin@example.com'])
    
    print("Database setup complete!")

if __name__ == '__main__':
    setup_database()