import requests
from bs4 import BeautifulSoup
import traceback

cached_teams = []

def get_all_teams():
    global cached_teams
    if cached_teams:
        return cached_teams

    base_url = "https://www.formula1.com"
    url = f"{base_url}/en/teams"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    team_cards = soup.select('a.group')
    teams = []

    for idx, card in enumerate(team_cards, start=1):
        try:
            team_name = card.select_one('span').text.strip()
            team_logo = card.select_one('img[src*="logo"]')['src']
            team_car_image = card.select('img[src*="/teams/"]')[-1]['src']
            team_points = card.select_one('div.flex.flex-col.gap-micro.items-end p').text.strip()

            driver_elements = card.select('.f1-team-driver-name')
            drivers = []
            for driver_elem in driver_elements:
                first = driver_elem.select_one('p:nth-of-type(1)').text.strip()
                last = driver_elem.select_one('p:nth-of-type(2)').text.strip()
                full = f"{first} {last}"
                drivers.append(full)

            team_url = f"{base_url}{card['href']}"
            team_response = requests.get(team_url, headers=headers)
            team_soup = BeautifulSoup(team_response.text, 'html.parser')

            def extract(label):
                element = team_soup.select_one(f'dt:contains("{label}") + dd')
                return element.text.strip() if element else "N/A"

            full_team_name = extract("Full Team Name")
            base = extract("Base")
            team_chief = extract("Team Chief")
            technical_chief = extract("Technical Chief")
            chassis = extract("Chassis")
            power_unit = extract("Power Unit")
            first_team_entry = extract("First Team Entry")
            world_championships = extract("World Championships")
            highest_race_finish = extract("Highest Race Finish")
            pole_positions = extract("Pole Positions")
            fastest_laps = extract("Fastest Laps")

            team_profile_elem = team_soup.select_one('.f1-atomic-wysiwyg')
            team_profile = team_profile_elem.text.strip() if team_profile_elem else "No profile available"

            team_data = {
                'team_id': idx,
                'team_name': team_name,
                'team_logo': team_logo,
                'team_car_image': team_car_image,
                'team_points': int(team_points),
                'drivers': drivers,
                'full_team_name': full_team_name,
                'base': base,
                'team_chief': team_chief,
                'technical_chief': technical_chief,
                'chassis': chassis,
                'power_unit': power_unit,
                'first_team_entry': first_team_entry,
                'world_championships': world_championships,
                'highest_race_finish': highest_race_finish,
                'pole_positions': pole_positions,
                'fastest_laps': fastest_laps,
                'team_profile': team_profile
            }

            teams.append(team_data)

        except Exception as e:
            print(f"[ERROR] Skipping team #{idx} due to error: {e}")
            traceback.print_exc()
            continue

    teams_sorted = sorted(teams, key=lambda x: x['team_name'].lower())

    for idx, team in enumerate(teams_sorted, start=1):
        team['team_id'] = idx

    cached_teams = teams_sorted
    return teams_sorted

def get_team_by_id(team_id):
    return next((t for t in get_all_teams() if t['team_id'] == team_id), None)

def get_team_by_driver(driver_name):
    driver_name = driver_name.lower()
    for team in get_all_teams():
        if any(driver_name in d.lower() for d in team['drivers']):
            return team
    return None

def get_teams_sorted_by_points():
    return sorted(get_all_teams(), key=lambda x: x['team_points'], reverse=True)

def get_top_teams(n=3):
    return get_teams_sorted_by_points()[:n]

def search_teams(query):
    query = query.lower()
    results = []
    for team in get_all_teams():
        if query in team['team_name'].lower() or any(query in d.lower() for d in team['drivers']):
            results.append(team)
    return results

def clear_cache():
    global cached_teams
    cached_teams = []
