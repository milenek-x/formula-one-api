import requests
from bs4 import BeautifulSoup
from races import get_all_race_urls

cached_circuits = {}

def get_circuit_info(circuit_url):
    circuit_url = f"{circuit_url}/circuit"
    global cached_circuits
    if circuit_url in cached_circuits:
        return cached_circuits[circuit_url]

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(circuit_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    circuit = {}

    # Circuit Name
    name_tag = soup.select_one('.f1-heading__body div')
    circuit['name'] = name_tag.get_text(strip=True) if name_tag else None

    # Image
    img_tag = soup.select_one("img[alt$='Circuit.png']")
    circuit['image_url'] = img_tag['src'] if img_tag else None

    # Track facts
    fact_titles = ['first_grand_prix', 'number_of_laps', 'circuit_length_km', 'race_distance_km', 'lap_record']
    fact_tags = soup.select('.f1-grid .f1-heading')
    for label, tag in zip(fact_titles, fact_tags):
        circuit[label] = tag.get_text(strip=True)

    # Description section (Optional: Try to find interesting info)
    prose = soup.select_one('.prose')
    if prose:
        sub_info = {}
        headers = prose.find_all(['h2', 'h3'])
        paragraphs = prose.find_all('p')

        for heading, para in zip(headers[1:], paragraphs):  # Skipping first heading
            key = heading.get_text(strip=True).lower().replace(' ', '_').replace('?', '')
            value = para.get_text(strip=True)
            sub_info[key] = value

        circuit['details'] = sub_info

    # Cache result
    cached_circuits[circuit_url] = circuit
    return circuit

def update_circuits_for_all_races():
    race_urls = get_all_race_urls()  # Get all race URLs
    all_circuits = []
    
    # Loop through each race URL and get circuit info
    for url in race_urls:
        circuit_info = get_circuit_info(url)
        all_circuits.append(circuit_info)

    # Optionally return all circuits if you need to return a jsonify message
    return all_circuits

def clear_cache():
    global cached_circuits
    cached_circuits = {}
