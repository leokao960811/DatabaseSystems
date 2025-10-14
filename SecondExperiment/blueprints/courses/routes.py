# blueprints/courses/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from .__init__ import courses_bp

def get_db_query_executor():
    return current_app.execute_query

@courses_bp.route('/', methods=['GET', 'POST'])
def manage_courses():
    execute_query = get_db_query_executor()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        time = request.form['time']
        department_id = request.form.get('department_id')
        if department_id == '':
            department_id = None

        query = "INSERT INTO Course (name, description, time, department_id) VALUES (%s, %s, %s, %s)"
        params = (name, description, time, department_id)
        
        if execute_query(query, params, commit=True):
            flash('Course added successfully!', 'success')
        else:
            flash('Error adding course.', 'danger')
        return redirect(url_for('courses.manage_courses'))

    courses = execute_query("SELECT * FROM Course")
    departments = execute_query("SELECT department_id, name FROM Department")
    return render_template('courses/courses.html', courses=courses, departments=departments)

@courses_bp.route('/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    execute_query = get_db_query_executor()
    mysql = current_app.mysql

    try:
        execute_query("DELETE FROM User_Courses WHERE course_id = %s", (course_id,), commit=True)

        if execute_query("DELETE FROM Course WHERE course_id = %s", (course_id,), commit=True):
            cur = mysql.connection.cursor()
            if cur.rowcount == 0:
                flash('Course not found.', 'danger')
            else:
                flash('Course deleted successfully!', 'success')
            cur.close()
        else:
            flash('Error deleting course.', 'danger')
    except Exception as e:
        flash(f'Error deleting course: {e}', 'danger')
    return redirect(url_for('courses.manage_courses'))