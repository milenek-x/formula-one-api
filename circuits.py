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
        text = tag.get_text(strip=True)
        if label == 'lap_record':
            # Process lap_record into time, driver, and year
            lap_record_time, lap_record_driver, lap_record_year = process_lap_record(text)
            circuit['lap_record_time'] = lap_record_time
            circuit['lap_record_driver'] = lap_record_driver
            circuit['lap_record_year'] = lap_record_year
        else:
            circuit[label] = text

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

def process_lap_record(lap_record_str):
    """
    Given a lap record string like '1:30.965Kimi Antonelli(2025)', 
    this function returns the lap time, driver name, and year.
    """
    # Regular expression to extract time, driver name, and year
    match = re.match(r'(\d+:\d+\.\d+)([A-Za-z\s]+)\((\d{4})\)', lap_record_str)
    if match:
        lap_record_time = match.group(1)  # "1:30.965"
        lap_record_driver = match.group(2).strip()  # "Kimi Antonelli"
        lap_record_year = match.group(3)  # "2025"
        return lap_record_time, lap_record_driver, lap_record_year
    else:
        # If the format is not correct, return None values
        return None, None, None

def clear_cache():
    global cached_circuits
    cached_circuits = {}
