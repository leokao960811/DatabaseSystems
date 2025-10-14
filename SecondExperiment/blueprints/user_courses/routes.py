# blueprints/user_courses/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from .__init__ import user_courses_bp

def get_db_query_executor():
    return current_app.execute_query

@user_courses_bp.route('/', methods=['GET', 'POST'])
def manage_user_courses():
    execute_query = get_db_query_executor()
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        course_id = request.form['course_id']
        
        query = "INSERT INTO User_Courses (user_id, course_id) VALUES (%s, %s)"
        params = (user_id, course_id)
        
        if execute_query(query, params, commit=True):
            flash('User joined course successfully!', 'success')
        else:
            flash('Error joining user to course (possibly already joined or invalid IDs).', 'danger')
        return redirect(url_for('user_courses.manage_user_courses'))

    user_courses = execute_query("""
        SELECT
            UC.user_id,
            UC.course_id,
            U.account_name,
            C.name AS course_name
        FROM
            User_Courses AS UC
        JOIN User AS U ON UC.user_id = U.user_id
        JOIN Course AS C ON UC.course_id = C.course_id
    """)
    users = execute_query("SELECT user_id, account_name FROM User")
    courses = execute_query("SELECT course_id, name FROM Course")
    return render_template('user_courses/user_courses.html', user_courses=user_courses, users=users, courses=courses)

@user_courses_bp.route('/delete/<int:user_id>/<int:course_id>', methods=['POST'])
def delete_user_course(user_id, course_id):
    execute_query = get_db_query_executor()
    if execute_query("DELETE FROM User_Courses WHERE user_id = %s AND course_id = %s", (user_id, course_id), commit=True):
        flash('User removed from course successfully!', 'success')
    else:
        flash('Error removing user from course.', 'danger')
    return redirect(url_for('user_courses.manage_user_courses'))