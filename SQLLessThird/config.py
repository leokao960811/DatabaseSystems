# config.py
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ITEM_HERE'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/notes'