# blueprints/departments/__init__.py

from flask import Blueprint

departments_bp = Blueprint('departments', __name__, template_folder='templates')