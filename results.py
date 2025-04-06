import requests
from bs4 import BeautifulSoup
from races import get_all_race_urls
from sessions import get_race_sessions

def parse_session_results(session_url):
    # Fetch the session page content
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(session_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize a list to store results
    results = []

    # Find the table that contains the results
    table = soup.find('table', class_='f1-table')

    if table:
        rows = table.find_all('tr', class_=['bg-brand-white', 'bg-grey-10'])  # Find rows with result data
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 7:  # Ensure we have all the required columns
                result = {
                    'position': cols[0].get_text(strip=True),
                    'number': cols[1].get_text(strip=True),
                    'driver': cols[2].get_text(strip=True),
                    'car': cols[3].get_text(strip=True),
                    'time': cols[4].get_text(strip=True),
                    'gap': cols[5].get_text(strip=True),
                    'laps': cols[6].get_text(strip=True)
                }
                results.append(result)
    
    return results

def get_results_for_races():
    # Get all races
    race_docs = db.collection('races').stream()

    # Loop through each race document
    for doc in race_docs:
        race = doc.to_dict()
        race_url = race.get('link')  # Get the race URL (link)
        if not race_url:
            print(f"Skipping race {race.get('name')}: No URL found.")
            continue

        # Fetch the sessions for this race
        sessions = get_race_sessions(race_url)

        # Loop through sessions and fetch results
        for session in sessions:
            session_name = session.get('name', '').lower()

            if 'practice 1' in session_name:
                session_url = f"{race_url}/practice/1"
                session['results'] = parse_session_results(session_url)
            elif 'practice 2' in session_name:
                session_url = f"{race_url}/practice/2"
                session['results'] = parse_session_results(session_url)
            elif 'practice 3' in session_name:
                session_url = f"{race_url}/practice/3"
                session['results'] = parse_session_results(session_url)
            elif 'qualifying' in session_name:
                session_url = f"{race_url}/starting-grid"
                session['results'] = parse_session_results(session_url)
            elif 'race' in session_name:
                session_url = f"{race_url}/race-result"
                session['results'] = parse_session_results(session_url)
            elif 'sprint' in session_name:
                session_url = f"{race_url}/sprint-result"
                session['results'] = parse_session_results(session_url)
            elif 'sprint qualifying' in session_name:
                session_url = f"{race_url}/sprint-grid"
                session['results'] = parse_session_results(session_url)
            else:
                print(f"Unknown session type: {session_name}")
                continue

            # Update session with results in the race document
            try:
                db.collection('races').document(doc.id).update({
                    'sessions': [session for session in sessions]
                })
                print(f"Updated session results for {session_name} in race {race.get('name')}")
            except Exception as e:
                print(f"Failed to update sessions for race {race.get('name')}: {e}")

