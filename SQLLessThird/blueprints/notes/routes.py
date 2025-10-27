# blueprints/notes/routes.py
from flask import render_template, request, redirect, url_for, current_app, flash
from . import notes_bp 
from datetime import datetime
from bson.objectid import ObjectId
import json

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

@notes_bp.route('/bulk_create', methods=['GET', 'POST'])
def bulk_create_notes():
    # Default JSON prompt for bulk creation
    default_json_prompt = json.dumps([
        {
            "text": "Meeting with John",
            "appointed_time": "2024-03-15T10:00"
        },
        {
            "text": "Review project proposal"
        },
        {
            "text": "Send weekly report",
            "appointed_time": "2024-03-10T17:00"
        }
    ], indent=2) # indent for pretty printing in the textarea

    if request.method == 'POST':
        json_data_raw = request.form.get('json_notes')

        if not json_data_raw:
            flash('JSON input is required!', 'danger')
            return render_template('notes/bulk_create.html', default_json_prompt=default_json_prompt)

        try:
            notes_data_list = json.loads(json_data_raw)
            if not isinstance(notes_data_list, list):
                raise ValueError("JSON must be an array of note objects.")
        except json.JSONDecodeError:
            flash('Invalid JSON format. Please check your syntax.', 'danger')
            return render_template('notes/bulk_create.html', default_json_prompt=default_json_prompt)
        except ValueError as e:
            flash(f'JSON input error: {e}', 'danger')
            return render_template('notes/bulk_create.html', default_json_prompt=default_json_prompt)

        notes_to_insert = []
        errors = []

        for i, note_dict in enumerate(notes_data_list):
            if not isinstance(note_dict, dict):
                errors.append(f"Item {i+1}: Expected a dictionary for note, got {type(note_dict).__name__}.")
                continue

            text = note_dict.get('text')
            appointed_time_str = note_dict.get('appointed_time')

            if not text:
                errors.append(f"Item {i+1}: 'text' field is required.")
                continue

            note_data = {
                'text': text,
                'time_created': datetime.utcnow()
            }

            if appointed_time_str:
                try:
                    note_data['appointed_time'] = datetime.strptime(appointed_time_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    errors.append(f"Item {i+1}: Invalid 'appointed_time' format. Use YYYY-MM-DDTHH:MM.")
                    continue
            
            notes_to_insert.append(note_data)
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            flash('Some notes could not be created due to errors.', 'danger')
            return render_template('notes/bulk_create.html', default_json_prompt=default_json_prompt)

        notes_collection = current_app.db.notes
        if notes_to_insert:
            notes_collection.insert_many(notes_to_insert)
            flash(f'{len(notes_to_insert)} note(s) created successfully!', 'success')
        else:
            flash('No valid notes were found in the JSON input.', 'warning')

        return redirect(url_for('notes.list_notes'))

    return render_template('notes/bulk_create.html', default_json_prompt=default_json_prompt)

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