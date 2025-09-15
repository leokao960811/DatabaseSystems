import os
from flask import Flask, render_template, request, redirect
import mysql.connector
from dotenv import load_dotenv

app = Flask(__name__, template_folder=r'D:\Programmed Files\Python\DatabaseSystem\FirstTest\templates')

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

# 首頁：顯示留言
@app.route("/")
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", messages=messages)

# 新增留言
@app.route("/add", methods=["POST"])
def add_message():
    name = request.form["name"]
    content = request.form["content"]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (name, content) VALUES (%s, %s)", (name, content))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)