# blueprints/notes/routes.py
from flask import render_template, request, redirect, url_for, current_app, flash
from . import notes_bp 
from datetime import datetime
from bson.objectid import ObjectId

@notes_bp.route('/')
def list_notes():
    notes_collection = current_app.db.notes
    notes = notes_collection.find().sort('time_created', -1) # Sort by creation time, newest first
    return render_template('notes/index.html', notes=notes)

@notes_bp.route('/create', methods=['GET', 'POST'])
def create_note():
    if request.method == 'POST':
        note_text = request.form.get('text')
        appointed_time_str = request.form.get('appointed_time')

        if not note_text:
            flash('Note text is required!', 'danger')
            return redirect(url_for('notes.create_note'))

        note_data = {
            'text': note_text,
            'time_created': datetime.utcnow()
        }

        if appointed_time_str:
            try:
                # Assuming input format is YYYY-MM-DDTHH:MM
                note_data['appointed_time'] = datetime.strptime(appointed_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid appointed time format. Please use YYYY-MM-DDTHH:MM.', 'danger')
                return redirect(url_for('notes.create_note'))

        notes_collection = current_app.db.notes
        notes_collection.insert_one(note_data)
        flash('Note created successfully!', 'success')
        return redirect(url_for('notes.list_notes'))
    return render_template('notes/create.html')

@notes_bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_note(id):
    notes_collection = current_app.db.notes
    note = notes_collection.find_one({'_id': ObjectId(id)})

    if not note:
        flash('Note not found!', 'danger')
        return redirect(url_for('notes.list_notes'))

    if request.method == 'POST':
        note_text = request.form.get('text')
        appointed_time_str = request.form.get('appointed_time')

        if not note_text:
            flash('Note text is required!', 'danger')
            return redirect(url_for('notes.edit_note', id=id))

        update_data = {
            'text': note_text
        }

        if appointed_time_str:
            try:
                update_data['appointed_time'] = datetime.strptime(appointed_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid appointed time format. Please use YYYY-MM-DDTHH:MM.', 'danger')
                return redirect(url_for('notes.edit_note', id=id))
        else:
            # If appointed time is cleared, remove it from the document
            notes_collection.update_one({'_id': ObjectId(id)}, {'$unset': {'appointed_time': ''}})
            update_data.pop('appointed_time', None) # Remove from update_data if it was set

        notes_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        flash('Note updated successfully!', 'success')
        return redirect(url_for('notes.list_notes'))

    # Format appointed_time for the HTML input field
    if 'appointed_time' in note and note['appointed_time']:
        note['appointed_time_str'] = note['appointed_time'].strftime('%Y-%m-%dT%H:%M')
    else:
        note['appointed_time_str'] = ''

    return render_template('notes/edit.html', note=note)

@notes_bp.route('/delete/<id>', methods=['POST'])
def delete_note(id):
    notes_collection = current_app.db.notes
    result = notes_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        flash('Note deleted successfully!', 'success')
    else:
        flash('Note not found!', 'danger')
    return redirect(url_for('notes.list_notes'))