from flask import Flask, jsonify, request
import os
import firebase_admin
from firebase_admin import credentials, firestore, db as firebase_db
from datetime import datetime, timedelta
from races import get_all_races, get_race_by_id, clear_cache as clear_race_cache, search_races
from drivers import (
    get_all_drivers, get_driver_by_id, get_drivers_by_team,
    get_top_drivers, get_drivers_sorted_by_points,
    search_drivers, clear_cache as clear_driver_cache
)
from sessions import get_race_sessions, clear_cache as clear_session_cache
from teams import (
    get_all_teams, get_team_by_id, get_team_by_driver,
    get_teams_sorted_by_points, get_top_teams, search_teams,
    clear_cache as clear_team_cache
)
# from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)

# Firebase setup
firebase_key_path = os.getenv('FIREBASE_KEY_PATH')

if not firebase_key_path:
    raise Exception("FIREBASE_KEY_PATH environment variable is not set.")

cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)

# Firestore DB
db = firestore.client()

# === HELPER FUNCTIONS ===
def is_data_fresh(collection_name):
    # Check if data is fresh (updated within the last 30 minutes)
    doc_ref = db.collection(collection_name).document('metadata')
    doc = doc_ref.get()
    
    if doc.exists:
        last_updated = doc.to_dict().get('last_updated')
        if last_updated:
            last_updated_time = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_updated_time < timedelta(minutes=30):
                return True
    return False

def update_timestamp(collection_name):
    # Update timestamp in Firestore
    doc_ref = db.collection(collection_name).document('metadata')
    doc_ref.set({
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

def fetch_from_firestore(collection_name):
    # Fetch all documents from Firestore
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    return [doc.to_dict() for doc in docs]

def upload_to_firestore(collection_name, data):
    # Upload data to Firestore
    collection_ref = db.collection(collection_name)
    for item in data:
        collection_ref.add(item)

# === RACE ENDPOINTS ===
@app.route('/api/schedule', methods=['GET'])
def api_get_schedule():
    # Fetch schedule from Firebase if data is fresh, else scrape and update Firebase
    if is_data_fresh('races'):
        races = fetch_from_firestore('races')
        return jsonify(races)
    else:
        # Scrape data and upload to Firebase
        races = get_all_races()
        upload_to_firestore('races', races)
        update_timestamp('races')
        return jsonify(races)

@app.route('/api/schedule/<int:race_id>', methods=['GET'])
def api_get_race_by_id(race_id):
    race = get_race_by_id(race_id)
    return jsonify(race) if race else jsonify({'error': 'Race not found'}), 404

@app.route('/api/schedule/search', methods=['GET'])
def api_search_schedule():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Missing query parameter ?q='}), 400
    results = search_races(query)
    return jsonify(results) if results else jsonify({'message': 'No matching races found.'}), 404

@app.route('/api/schedule/cache/clear', methods=['POST'])
def api_clear_schedule_cache():
    clear_race_cache()
    return jsonify({'message': 'Schedule cache cleared.'})

# === SESSION ENDPOINTS ===
@app.route('/api/schedule/<int:race_id>/sessions', methods=['GET'])
def api_get_race_sessions(race_id):
    sessions = get_race_sessions(race_id)
    return jsonify(sessions) if sessions else jsonify({'error': 'Race or sessions not found'}), 404

@app.route('/api/sessions/cache/clear', methods=['POST'])
def api_clear_session_cache():
    clear_session_cache()
    return jsonify({'message': 'Session cache cleared.'})

# === DRIVER ENDPOINTS ===
@app.route('/api/drivers', methods=['GET'])
def api_get_all_drivers():
    if is_data_fresh('drivers'):
        drivers = fetch_from_firestore('drivers')
        return jsonify(drivers)
    else:
        drivers = get_all_drivers()
        upload_to_firestore('drivers', drivers)
        update_timestamp('drivers')
        return jsonify(drivers)

@app.route('/api/driver/<int:driver_id>', methods=['GET'])
def api_get_driver_by_id(driver_id):
    driver = get_driver_by_id(driver_id)
    return jsonify(driver) if driver else jsonify({'error': 'Driver not found'}), 404

@app.route('/api/drivers/team/<string:team_name>', methods=['GET'])
def api_get_drivers_by_team(team_name):
    team_drivers = get_drivers_by_team(team_name)
    return jsonify(team_drivers) if team_drivers else jsonify({'error': 'No drivers found for team'}), 404

@app.route('/api/drivers/sorted/points', methods=['GET'])
def api_get_sorted_drivers():
    return jsonify(get_drivers_sorted_by_points())

@app.route('/api/drivers/top3', methods=['GET'])
def api_get_top3_drivers():
    return jsonify(get_top_drivers())

@app.route('/api/drivers/search', methods=['GET'])
def api_search_drivers():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Missing query parameter ?q='}), 400
    results = search_drivers(query)
    return jsonify(results) if results else jsonify({'message': 'No matching drivers found.'}), 404

@app.route('/api/drivers/cache/clear', methods=['POST'])
def api_clear_driver_cache():
    clear_driver_cache()
    return jsonify({"message": "Driver cache cleared."})

# === TEAM ENDPOINTS ===
@app.route('/api/teams', methods=['GET'])
def api_get_teams():
    if is_data_fresh('teams'):
        teams = fetch_from_firestore('teams')
        return jsonify(teams)
    else:
        teams = get_all_teams()
        upload_to_firestore('teams', teams)
        update_timestamp('teams')
        return jsonify(teams)

@app.route('/api/teams/<int:team_id>', methods=['GET'])
def api_get_team_by_id(team_id):
    team = get_team_by_id(team_id)
    return jsonify(team) if team else jsonify({'message': 'Team not found'}), 404

@app.route('/api/teams/driver', methods=['GET'])
def api_get_team_by_driver():
    driver_name = request.args.get('name', '').lower()
    if not driver_name:
        return jsonify({'error': 'Missing query parameter ?name='}), 400
    team = get_team_by_driver(driver_name)
    return jsonify(team) if team else jsonify({'message': 'No team found for this driver'}), 404

@app.route('/api/teams/sort', methods=['GET'])
def api_sort_teams_by_points():
    return jsonify(get_teams_sorted_by_points())

@app.route('/api/teams/top3', methods=['GET'])
def api_get_top3_teams():
    return jsonify(get_top_teams())

@app.route('/api/teams/search', methods=['GET'])
def api_search_teams():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Missing query parameter ?q='}), 400
    results = search_teams(query)
    return jsonify(results) if results else jsonify({'message': 'No matching teams found.'}), 404

@app.route('/api/teams/cache/clear', methods=['POST'])
def api_clear_team_cache():
    clear_team_cache()
    return jsonify({"message": "Team cache cleared."})

# === ROOT ===
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "F1 API is running"})

if __name__ == '__main__':
    app.run(debug=True)
