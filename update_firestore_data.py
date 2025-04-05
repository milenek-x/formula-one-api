import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

from races import get_all_races
from drivers import get_all_drivers
from teams import get_all_teams

# Firebase setup
firebase_key_path = os.getenv('FIREBASE_KEY_PATH')

if not firebase_key_path:
    firebase_key_path = "firebase-key.json"
    cred = credentials.Certificate(firebase_key_path)
else:
    firebase_key_path_dict = json.loads(firebase_key_path)
    cred = credentials.Certificate(firebase_key_path_dict)

firebase_admin.initialize_app(cred)
db = firestore.client()

def upload_to_firestore(collection_name, data):
    collection_ref = db.collection(collection_name)

    # Clear old documents (except metadata)
    docs = collection_ref.stream()
    for doc in docs:
        if doc.id != 'metadata':
            doc.reference.delete()

    # Upload new data
    for item in data:
        collection_ref.add(item)

    # Update metadata
    collection_ref.document('metadata').set({
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

def update_all():
    print("Updating races...")
    races = get_all_races()
    upload_to_firestore('races', races)

    print("Updating drivers...")
    drivers = get_all_drivers()
    upload_to_firestore('drivers', drivers)

    print("Updating teams...")
    teams = get_all_teams()
    upload_to_firestore('teams', teams)

    print("Update complete.")

if __name__ == "__main__":
    update_all()
