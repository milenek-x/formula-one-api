import requests
from bs4 import BeautifulSoup
import traceback

cached_drivers = []

def get_all_drivers():
    global cached_drivers
    if cached_drivers:
        return cached_drivers

    base_url = "https://www.formula1.com"
    url = f"{base_url}/en/drivers.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    driver_cards = soup.select('a.group')
    drivers = []

    for idx, card in enumerate(driver_cards, start=1):
        try:
            first_name = card.select_one('.f1-driver-name p:nth-of-type(1)').text.strip()
            last_name = card.select_one('.f1-driver-name p:nth-of-type(2)').text.strip()
            full_name = f"{first_name} {last_name}"
            team = card.select_one('p.text-greyDark').text.strip()
            driver_points_elem = card.select_one('div.flex.flex-col.gap-micro.items-end p')
            driver_points = driver_points_elem.text.strip() if driver_points_elem else "0"
            nationality = card.select_one('img[alt][src*="flags"]')['alt']
            driver_image = card.select_one('img[src*="drivers"]')['src']
            number_logo = card.select_one('img[src*="number-logos"]')['src']
            profile_url = base_url + card['href']

            profile_response = requests.get(profile_url, headers=headers)
            profile_soup = BeautifulSoup(profile_response.text, 'html.parser')

            details = {}
            rows = profile_soup.select('div.f1-dl dl > dt')
            for dt in rows:
                label = dt.text.strip()
                dd = dt.find_next_sibling('dd')
                if dd:
                    value = dd.text.strip()
                    details[label] = value

            bio_section = profile_soup.select('div.f1-driver-bio .f1-atomic-wysiwyg p')
            bio_paragraphs = [p.text.strip() for p in bio_section]
            biography = "\n".join(bio_paragraphs)

            driver_data = {
                'driver_id': idx,
                'name': full_name,
                'team': team,
                'driver_points': int(driver_points),
                'nationality': nationality,
                'image': driver_image,
                'number_logo': number_logo,
                'profile_url': profile_url,
                'profile_data': details,
                'biography': biography
            }

            drivers.append(driver_data)

        except Exception as e:
            print(f"\n[ERROR] Skipping driver card #{idx} due to error:\n{e}")
            traceback.print_exc()
            continue

    drivers_sorted = sorted(drivers, key=lambda d: d['name'].split()[-1].lower())

    for idx, driver in enumerate(drivers_sorted, start=1):
        driver['driver_id'] = idx

    cached_drivers = drivers_sorted
    return drivers_sorted

def get_driver_by_id(driver_id):
    drivers = get_all_drivers()
    return next((d for d in drivers if d['driver_id'] == driver_id), None)

def get_drivers_by_team(team_name):
    drivers = get_all_drivers()
    return [d for d in drivers if d['team'].lower() == team_name.lower()]

def get_top_drivers(n=3):
    drivers = get_all_drivers()
    return sorted(drivers, key=lambda d: d['driver_points'], reverse=True)[:n]

def get_drivers_sorted_by_points():
    return sorted(get_all_drivers(), key=lambda d: d['driver_points'], reverse=True)

def search_drivers(query):
    query = query.lower()
    matches = []
    for d in get_all_drivers():
        if query in d['name'].lower() or query in d['team'].lower() or query in d['nationality'].lower():
            matches.append(d)
    return matches

def clear_cache():
    global cached_drivers
    cached_drivers = []
