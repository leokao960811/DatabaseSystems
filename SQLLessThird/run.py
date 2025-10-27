# app.py
from flask import Flask, render_template
from config import Config
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MongoDB
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.notes_db # Access the database named 'notes_db'

    # Register Blueprints
    from blueprints.notes import notes_bp
    app.register_blueprint(notes_bp, url_prefix='/notes')

    @app.route('/')
    def index():
        return render_template('index.html') 

    return app

app = create_app()

if __name__ == '__main__':
    
    app.run(debug=True)