# backend/tests/conftest.py
import sys
import os

# Add the backend folder to Python path so "modules.search" etc. can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))