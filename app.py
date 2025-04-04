from flask import Flask, jsonify, request
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from races import get_race_by_id, search_races, clear_cache as clear_race_cache
from drivers import get_driver_by_id, get_drivers_by_team, get_top_drivers, get_drivers_sorted_by_points, search_drivers, clear_cache as clear_driver_cache
from sessions import get_race_sessions, clear_cache as clear_session_cache
from teams import get_team_by_id, get_team_by_driver, get_teams_sorted_by_points, get_top_teams, search_teams, clear_cache as clear_team_cache
from circuits import get_circuit_info, clear_cache as clear_circuit_cache

app = Flask(__name__)

# === Firebase setup ===
firebase_key_path = os.getenv('FIREBASE_KEY_PATH')

# If running locally, fallback to loading the local JSON key
if not firebase_key_path:
    firebase_key_path = "C:/Users/User/OneDrive - National Institute of Business Management (1)/Personal/MAD/Coursework/formula-one-api.json"
    cred = credentials.Certificate(firebase_key_path)
else:
    firebase_key_path_dict = json.loads(firebase_key_path)
    cred = credentials.Certificate(firebase_key_path_dict)

firebase_admin.initialize_app(cred)
db = firestore.client()

# === Firestore read helper ===
def fetch_from_firestore(collection_name):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    return [doc.to_dict() for doc in docs if doc.id != "metadata"]

# === ROUTES ===

@app.route('/api/schedule', methods=['GET'])
def api_get_schedule():
    races = fetch_from_firestore('races')
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

@app.route('/api/schedule/<int:race_id>/sessions', methods=['GET'])
def api_get_race_sessions(race_id):
    race_ref = db.collection('races').where('race_id', '==', race_id).limit(1)
    race_snapshot = race_ref.get()

    if not race_snapshot:
        return jsonify({'error': f'Race with ID {race_id} not found.'}), 404

    race = race_snapshot[0].to_dict()
    race_url = race.get('url') or race.get('link')

    sessions = get_race_sessions(race_url)
    if sessions:
        db.collection('races').document(race_snapshot[0].id).update({'sessions': sessions})
        return jsonify(sessions)
    else:
        return jsonify({'error': 'No sessions found for this race.'}), 404

@app.route('/api/schedule/<int:race_id>/circuit', methods=['GET'])
def api_get_race_circuit(race_id):
    race_ref = db.collection('races').where('race_id', '==', race_id).limit(1)
    race_snapshot = race_ref.get()

    if not race_snapshot:
        return jsonify({'error': f'Race with ID {race_id} not found.'}), 404

    race_doc = race_snapshot[0]
    race = race_doc.to_dict()
    race_url = race.get('url') or race.get('link')

    try:
        circuit_info = get_circuit_info(race_url)
        db.collection('races').document(race_doc.id).update({'circuit': circuit_info})
        return jsonify(circuit_info)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch circuit info', 'details': str(e)}), 500

@app.route('/api/circuits/cache/clear', methods=['POST'])
def api_clear_circuit_cache():
    clear_circuit_cache()
    return jsonify({'message': 'Circuit cache cleared.'})

@app.route('/api/drivers', methods=['GET'])
def api_get_all_drivers():
    drivers = fetch_from_firestore('drivers')
    return jsonify(drivers)

@app.route('/api/driver/<int:driver_id>', methods=['GET'])
def api_get_driver_by_id(driver_id):
    driver = get_driver_by_id(driver_id)
    return jsonify(driver) if driver else jsonify({'error': 'Driver not found'}), 404

@app.route('/api/drivers/team/<string:team_name>', methods=['GET'])
def api_get_drivers_by_team(team_name):
    drivers = get_drivers_by_team(team_name)
    return jsonify(drivers) if drivers else jsonify({'error': 'No drivers found'}), 404

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

@app.route('/api/teams', methods=['GET'])
def api_get_teams():
    teams = fetch_from_firestore('teams')
    return jsonify(teams)

@app.route('/api/teams/<int:team_id>', methods=['GET'])
def api_get_team_by_id(team_id):
    team = get_team_by_id(team_id)
    return jsonify(team) if team else jsonify({'error': 'Team not found'}), 404

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

@app.route('/api/sessions/cache/clear', methods=['POST'])
def api_clear_session_cache():
    clear_session_cache()
    return jsonify({'message': 'Session cache cleared.'})

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "F1 API is running"})

if __name__ == '__main__':
    app.run(debug=True)
