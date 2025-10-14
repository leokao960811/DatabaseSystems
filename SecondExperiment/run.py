# run.py

from flask import Flask, render_template
from flask_mysqldb import MySQL
from config import Config

# Import blueprints
from blueprints.departments.routes import departments_bp
from blueprints.users.routes import users_bp
from blueprints.courses.routes import courses_bp
from blueprints.joined_views.routes import joined_views_bp
from blueprints.user_courses.routes import user_courses_bp

# Import database commands
from db_commands import db as db_cli_group # Import the Click group

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'supersecretkey'

mysql = MySQL(app)

# --- Helper Function for Database Operations ---
def execute_query(query, params=None, fetch_one=False, commit=False):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query, params)
        if commit:
            mysql.connection.commit()
            cur.close()
            return True
        else:
            result = cur.fetchone() if fetch_one else cur.fetchall()
            cur.close()
            return result
    except Exception as e:
        print(f"Database error: {e}")
        if commit:
            mysql.connection.rollback()
        return None

# Make the execute_query function and mysql object available to blueprints and CLI commands
app.execute_query = execute_query
app.mysql = mysql

# Register Blueprints
app.register_blueprint(departments_bp, url_prefix='/ui/departments')
app.register_blueprint(users_bp, url_prefix='/ui/users')
app.register_blueprint(courses_bp, url_prefix='/ui/courses')
app.register_blueprint(user_courses_bp, url_prefix='/ui/user_courses')
app.register_blueprint(joined_views_bp, url_prefix='/ui/joined')

# Register CLI commands
app.cli.add_command(db_cli_group) # Register the 'db' Click group

# --- Global Routes (e.g., homepage) ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)