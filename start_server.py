#!/usr/bin/env python3
"""
Simple script to start the Django server with proper error handling
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Start the Django development server."""
    try:
        # Set the Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        if os.path.exists(backend_dir):
            os.chdir(backend_dir)
            print(f"Changed to directory: {os.getcwd()}")
        
        # Setup Django
        django.setup()
        print("Django setup completed")
        
        # Start the server
        print("Starting Django development server...")
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
        
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
