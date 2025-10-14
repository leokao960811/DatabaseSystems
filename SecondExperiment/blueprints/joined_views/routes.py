# blueprints/joined_views/routes.py

from flask import render_template, current_app
from .__init__ import joined_views_bp

def get_db_query_executor():
    return current_app.execute_query

@joined_views_bp.route('/users_departments')
def users_departments():
    execute_query = get_db_query_executor()
    query = """
        SELECT
            U.user_id,
            U.account_name,
            U.email_address,
            D.name AS department_name
        FROM
            User AS U
        LEFT JOIN
            Department AS D ON U.department_id = D.department_id
    """
    data = execute_query(query)
    return render_template('joined_views/joined_users_departments.html', data=data)

@joined_views_bp.route('/departments_courses')
def departments_courses():
    execute_query = get_db_query_executor()
    query = """
        SELECT
            D.department_id,
            D.name AS department_name,
            C.course_id,
            C.name AS course_name,
            C.description,
            C.time
        FROM
            Department AS D
        LEFT JOIN
            Course AS C ON D.department_id = C.department_id
    """
    data = execute_query(query)
    return render_template('joined_views/joined_departments_courses.html', data=data)

@joined_views_bp.route('/users_courses')
def users_courses():
    execute_query = get_db_query_executor()
    query = """
        SELECT
            U.user_id,
            U.account_name,
            C.course_id,
            C.name AS course_name,
            C.time
        FROM
            User AS U
        JOIN
            User_Courses AS UC ON U.user_id = UC.user_id
        JOIN
            Course AS C ON UC.course_id = C.course_id
    """
    data = execute_query(query)
    return render_template('joined_views/joined_users_courses.html', data=data)

@joined_views_bp.route('/all')
def all_joined_data():
    execute_query = get_db_query_executor()
    query = """
        SELECT
            U.user_id,
            U.account_name,
            U.email_address,
            D_User.name AS user_department_name,
            C.course_id,
            C.name AS course_name,
            C.time,
            D_Course.name AS course_offering_department
        FROM
            User AS U
        LEFT JOIN
            Department AS D_User ON U.department_id = D_User.department_id
        LEFT JOIN
            User_Courses AS UC ON U.user_id = UC.user_id
        LEFT JOIN
            Course AS C ON UC.course_id = C.course_id
        LEFT JOIN
            Department AS D_Course ON C.department_id = D_Course.department_id
        ORDER BY U.user_id, C.course_id;
    """
    data = execute_query(query)
    return render_template('joined_views/joined_all.html', data=data)