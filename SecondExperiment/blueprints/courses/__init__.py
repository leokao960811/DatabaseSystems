# blueprints/courses/__init__.py

from flask import Blueprint

courses_bp = Blueprint('courses', __name__, template_folder='templates')