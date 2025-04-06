import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

from races import get_all_races, get_all_race_urls
from drivers import get_all_drivers
from teams import get_all_teams
from circuits import get_circuit_info
from sessions import get_race_sessions


# Firebase setup
firebase_key_path = os.getenv('FIREBASE_KEY_PATH')

if not firebase_admin._apps:
    # If running locally, fallback to loading the local JSON key
    if not firebase_key_path:
        firebase_key_path = "C:/Users/User/OneDrive - National Institute of Business Management (1)/Personal/MAD/Coursework/formula-one-api.json"
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

def update_races():
    print("Updating races...")
    races = get_all_races()
    upload_to_firestore('races', races)

def update_drivers():
    print("Updating drivers...")
    drivers = get_all_drivers()
    upload_to_firestore('drivers', drivers)

def update_teams():
    print("Updating teams...")
    teams = get_all_teams()
    upload_to_firestore('teams', teams)

def update_circuits():
    print("Updating circuits...")
    race_docs = db.collection('races').stream()

    for doc in race_docs:
        race = doc.to_dict()
        race_url = race.get('url') or race.get('link')
        if not race_url:
            continue

        try:
            circuit_info = get_circuit_info(race_url)
            docs = list(db.collection('races').where('link', '==', race_url).limit(1).stream())
            if docs:
                docs[0].reference.update({'circuit': circuit_info})
            else:
                print(f"No race found with link: {race_url}")
            print(f"Updated circuit for race: {race.get('name')}")
        except Exception as e:
            print(f"Failed to update circuit for race {race.get('name')}: {e}")

def update_sessions():
    print("Updating sessions...")
    race_docs = db.collection('races').stream()

    for doc in race_docs:
        race = doc.to_dict()
        race_url = race.get('url') or race.get('link')
        if not race_url:
            continue

        try:
            sessions = get_race_sessions(race_url)
            if sessions:
                docs = list(db.collection('races').where('link', '==', race_url).limit(1).stream())
                if docs:
                    docs[0].reference.update({'sessions': sessions})
                else:
                    print(f"No race found with link: {race_url}")
                # db.collection('races').document(doc.id).update({'sessions': sessions})
                print(f"Updated sessions for race: {race.get('name')}")
        except Exception as e:
            print(f"Failed to update sessions for race {race.get('name')}: {e}")


def update_all():
    update_races()
    update_drivers()
    update_teams()
    update_circuits()
    update_sessions()
    print("Update complete.")


if __name__ == "__main__":
    update_all()
