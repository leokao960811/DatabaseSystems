# blueprints/users/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from .__init__ import users_bp

def get_db_query_executor():
    return current_app.execute_query

@users_bp.route('/', methods=['GET', 'POST'])
def manage_users():
    execute_query = get_db_query_executor()
    
    if request.method == 'POST':
        account_name = request.form['account_name']
        email_address = request.form['email_address']
        department_id = request.form.get('department_id')
        if department_id == '':
            department_id = None

        query = "INSERT INTO User (account_name, email_address, department_id) VALUES (%s, %s, %s)"
        params = (account_name, email_address, department_id)
        
        if execute_query(query, params, commit=True):
            flash('User added successfully!', 'success')
        else:
            flash('Error adding user.', 'danger')
        return redirect(url_for('users.manage_users'))

    users = execute_query("SELECT * FROM User")
    departments = execute_query("SELECT department_id, name FROM Department")
    return render_template('users/users.html', users=users, departments=departments)

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    execute_query = get_db_query_executor()
    mysql = current_app.mysql

    try:
        execute_query("DELETE FROM User_Courses WHERE user_id = %s", (user_id,), commit=True)
        
        if execute_query("DELETE FROM User WHERE user_id = %s", (user_id,), commit=True):
            cur = mysql.connection.cursor()
            if cur.rowcount == 0:
                flash('User not found.', 'danger')
            else:
                flash('User deleted successfully!', 'success')
            cur.close()
        else:
            flash('Error deleting user.', 'danger')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'danger')
    return redirect(url_for('users.manage_users'))