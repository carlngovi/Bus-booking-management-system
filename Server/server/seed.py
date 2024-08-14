from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def drop_all_tables():
    # Use the current app's engine to connect to the database
    engine = db.engine

    # Create a MetaData instance and reflect the existing database schema
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Drop all tables
    metadata.drop_all(bind=engine)
    print("All tables have been dropped.")

if __name__ == "__main__":
    with app.app_context():
        drop_all_tables()
