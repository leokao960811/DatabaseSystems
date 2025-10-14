# blueprints/departments/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from .__init__ import departments_bp # Import the blueprint instance

# Access the execute_query function from the current_app context
# This is a simple way to share the function without circular imports
def get_db_query_executor():
    return current_app.execute_query

@departments_bp.route('/', methods=['GET', 'POST'])
def manage_departments():
    execute_query = get_db_query_executor()
    
    if request.method == 'POST':
        name = request.form['name']
        if execute_query("INSERT INTO Department (name) VALUES (%s)", (name,), commit=True):
            flash('Department added successfully!', 'success')
        else:
            flash('Error adding department.', 'danger')
        return redirect(url_for('departments.manage_departments')) # Note: 'departments.manage_departments'

    departments = execute_query("SELECT * FROM Department")
    return render_template('departments/departments.html', departments=departments)

@departments_bp.route('/delete/<int:department_id>', methods=['POST'])
def delete_department(department_id):
    execute_query = get_db_query_executor()
    mysql = current_app.mysql # Access mysql object for rowcount

    try:
        execute_query("UPDATE User SET department_id = NULL WHERE department_id = %s", (department_id,), commit=True)
        execute_query("UPDATE Course SET department_id = NULL WHERE department_id = %s", (department_id,), commit=True)

        if execute_query("DELETE FROM Department WHERE department_id = %s", (department_id,), commit=True):
            # Check if any row was actually deleted
            cur = mysql.connection.cursor()
            if cur.rowcount == 0:
                flash('Department not found.', 'danger')
            else:
                flash('Department deleted successfully!', 'success')
            cur.close()
        else:
            flash('Error deleting department.', 'danger')
    except Exception as e:
        flash(f'Error deleting department: {e}', 'danger')
    return redirect(url_for('departments.manage_departments'))