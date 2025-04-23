import pytest
from dotenv import load_dotenv
import os

print("✅ conftest.py loaded") 

def load_env():
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    print(f"🔍 Looking for .env at: {dotenv_path}")
    
    if os.path.isfile(dotenv_path):
        print("✅ .env file found!")
    else:
        print("❌ .env file NOT found!")

    loaded = load_dotenv(dotenv_path)
    print(f"✅ .env loaded: {loaded}")

# Run this immediately when pytest starts
load_env()