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