#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env file in the backend directory
env_path = Path(__file__).resolve().parent / '.env'
try:
    load_dotenv(dotenv_path=env_path)
except Exception as e:
    print(f"Error loading .env file at {env_path}: {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
