# db_commands.py

import click
from flask.cli import with_appcontext
from flask import current_app

@click.group()
def db():
    """Manages database operations."""
    pass

@db.command('init')
@with_appcontext
def init_db_command():
    """Initializes the database tables based on the ER model."""
    mysql = current_app.mysql
    execute_query = current_app.execute_query

    try:
        # Drop tables in reverse order of dependency to avoid foreign key errors
        # (Optional: only if you want to re-create tables from scratch)
        click.echo("Dropping existing tables (if any)...")
        execute_query("DROP TABLE IF EXISTS User_Courses", commit=True)
        execute_query("DROP TABLE IF EXISTS User", commit=True)
        execute_query("DROP TABLE IF EXISTS Course", commit=True)
        execute_query("DROP TABLE IF EXISTS Department", commit=True)

        click.echo("Creating Department table...")
        execute_query("""
            CREATE TABLE Department (
                department_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            )
        """, commit=True)

        click.echo("Creating User table...")
        execute_query("""
            CREATE TABLE User (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                account_name VARCHAR(255) NOT NULL UNIQUE,
                email_address VARCHAR(255) NOT NULL UNIQUE,
                department_id INT,
                FOREIGN KEY (department_id) REFERENCES Department(department_id)
            )
        """, commit=True)

        click.echo("Creating Course table...")
        execute_query("""
            CREATE TABLE Course (
                course_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                time VARCHAR(100),
                department_id INT,
                FOREIGN KEY (department_id) REFERENCES Department(department_id)
            )
        """, commit=True)

        click.echo("Creating User_Courses (junction) table...")
        execute_query("""
            CREATE TABLE User_Courses (
                user_id INT,
                course_id INT,
                PRIMARY KEY (user_id, course_id),
                FOREIGN KEY (user_id) REFERENCES User(user_id),
                FOREIGN KEY (course_id) REFERENCES Course(course_id)
            )
        """, commit=True)

        click.echo("Database tables initialized successfully!")

    except Exception as e:
        click.echo(f"Error initializing database: {e}", err=True)
        # Rollback if any error occurred during table creation (though DDL is often auto-committed)
        mysql.connection.rollback()

@db.command('seed')
@with_appcontext
def seed_db_command():
    """Seeds the database with initial data."""
    execute_query = current_app.execute_query

    click.echo("Seeding database with sample data...")
    try:
        # Clear existing data (optional, but good for re-seeding)
        execute_query("DELETE FROM User_Courses", commit=True)
        execute_query("DELETE FROM User", commit=True)
        execute_query("DELETE FROM Course", commit=True)
        execute_query("DELETE FROM Department", commit=True)
        
        # Reset auto-increment counters (optional, for clean IDs)
        execute_query("ALTER TABLE Department AUTO_INCREMENT = 1", commit=True)
        execute_query("ALTER TABLE User AUTO_INCREMENT = 1", commit=True)
        execute_query("ALTER TABLE Course AUTO_INCREMENT = 1", commit=True)


        # Insert Departments
        execute_query("INSERT INTO Department (name) VALUES (%s)", ('Computer Science',), commit=True)
        execute_query("INSERT INTO Department (name) VALUES (%s)", ('Electrical Engineering',), commit=True)
        execute_query("INSERT INTO Department (name) VALUES (%s)", ('Mathematics',), commit=True)
        
        # Insert Users
        execute_query("INSERT INTO User (account_name, email_address, department_id) VALUES (%s, %s, %s)", ('john_doe', 'john.doe@example.com', 1), commit=True)
        execute_query("INSERT INTO User (account_name, email_address, department_id) VALUES (%s, %s, %s)", ('jane_smith', 'jane.smith@example.com', 1), commit=True)
        execute_query("INSERT INTO User (account_name, email_address, department_id) VALUES (%s, %s, %s)", ('bob_johnson', 'bob.j@example.com', 2), commit=True)

        # Insert Courses
        execute_query("INSERT INTO Course (name, description, time, department_id) VALUES (%s, %s, %s, %s)", ('Intro to SQL', 'Learn the basics of SQL.', 'Mon/Wed 10:00 AM', 1), commit=True)
        execute_query("INSERT INTO Course (name, description, time, department_id) VALUES (%s, %s, %s, %s)", ('Advanced Python', 'Deep dive into Python programming.', 'Tue/Thu 2:00 PM', 1), commit=True)
        execute_query("INSERT INTO Course (name, description, time, department_id) VALUES (%s, %s, %s, %s)", ('Circuit Design', 'Fundamentals of analog circuit design.', 'Mon/Wed 1:00 PM', 2), commit=True)

        # Insert User_Courses
        execute_query("INSERT INTO User_Courses (user_id, course_id) VALUES (%s, %s)", (1, 1), commit=True)
        execute_query("INSERT INTO User_Courses (user_id, course_id) VALUES (%s, %s)", (1, 2), commit=True)
        execute_query("INSERT INTO User_Courses (user_id, course_id) VALUES (%s, %s)", (2, 1), commit=True)

        click.echo("Database seeded successfully!")

    except Exception as e:
        click.echo(f"Error seeding database: {e}", err=True)
        mysql.connection.rollback()