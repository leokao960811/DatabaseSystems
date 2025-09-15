import os
from flask import Flask, render_template, request, redirect
import mysql.connector
from dotenv import load_dotenv

app = Flask(__name__, template_folder=r'D:\Programmed Files\Python\DatabaseSystem\DatabaseSystems\FirstTest\templates')

DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST")
DB_NAME=os.getenv("DB_NAME")

# Configure your MySQL connection
db_config = {
    "host": DB_HOST,
    "user": DB_USER,        # change if needed
    "password": DB_PASSWORD,# change if needed
    "database": DB_NAME   # must exist already
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    # Render the new main index.html template
    return render_template('index.html')

@app.route('/create_table')
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Drop the existing users table if it exists, so we can recreate it with the new schema
        # Be careful with this in production, as it deletes all data!
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()

        cursor.execute("""
            CREATE TABLE users (
                userID INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                time_of_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        return "Table 'users' created successfully with new schema!"
    except mysql.connector.Error as err:
        return f"Error creating table: {err}"
    finally:
        cursor.close()
        conn.close()

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username'] # Changed from 'name' to 'username'
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # userID is AUTO_INCREMENT, so we don't include it in the INSERT statement
            # time_of_creation uses DEFAULT CURRENT_TIMESTAMP, so we don't include it either
            cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
            conn.commit()
            return redirect(url_for('list_users'))
        except mysql.connector.Error as err:
            return f"Error adding user: {err}"
        finally:
            cursor.close()
            conn.close()
    return render_template('add_user.html')

@app.route('/users')
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # Returns rows as dictionaries
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)