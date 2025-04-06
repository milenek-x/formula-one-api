import requests
from bs4 import BeautifulSoup
import traceback

cached_races = []

def get_all_races():
    global cached_races
    if cached_races:
        return cached_races

    try:
        url = "https://www.formula1.com/en/racing/2025"
        base_url = "https://www.formula1.com"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        race_blocks = soup.find_all('a', class_='outline-offset-4')
        races_info = []

        for idx, race in enumerate(race_blocks, start=0):
            race_data = {'race_id': idx}

            round_info = race.find('p', class_='f1-text font-titillium tracking-normal font-bold non-italic uppercase leading-snug f1-text__micro text-fs-15px text-brand-primary')
            if round_info:
                race_data['round'] = round_info.get_text(strip=True)

            date_range = race.find('p', class_='f1-heading-wide font-formulaOneWide tracking-normal font-normal non-italic text-fs-18px leading-none normal-case text-brand-black')
            if date_range:
                race_data['date_range'] = date_range.get_text(strip=True)

            month = race.find('span', class_='f1-heading-wide font-formulaOneWide tracking-normal font-normal non-italic text-fs-12px leading-none uppercase inline-flex items-center px-xs py-micro rounded-xxs bg-brand-black text-brand-white')
            if month:
                race_data['month'] = month.get_text(strip=True)

            grand_prix_name = race.find('p', class_='f1-heading tracking-normal text-fs-18px leading-tight normal-case font-bold non-italic f1-heading__body font-formulaOne overflow-hidden')
            if grand_prix_name:
                race_data['grand_prix_name'] = grand_prix_name.get_text(strip=True)

            location = race.find('p', class_='f1-heading tracking-normal text-fs-12px leading-tight normal-case font-normal non-italic f1-heading__body font-formulaOne')
            if location:
                race_data['location'] = location.get_text(strip=True)

            grand_prix_link = race.get('href')
            if grand_prix_link:
                full_link = f"{base_url}{grand_prix_link}"
                race_data['link'] = full_link

            wrapper = race.find('div', class_='grid grid-cols-none tablet:inline-flex gap-1')

            if wrapper:
                # Step 2: Find the first <a> inside this div
                result_link_tag = wrapper.find('a', attrs={'data-path': True})

                if result_link_tag:
                    result_link = result_link_tag['data-path']


            flag_img = race.find('img', class_='f1-c-image h-[1.625rem]')
            if flag_img:
                race_data['flag_image'] = flag_img.get('src')

            circuit_img = race.find('img', class_='f1-c-image h-[110px] w-full object-cover')
            if circuit_img:
                race_data['circuit_image'] = circuit_img.get('src')

            # ========== PODIUM EXTRACTION ==========
            podium_section = race.find('div', class_='h-[110px] grid grid-cols-3 gap-micro items-end')
            if podium_section:
                podium = []
                podium_divs = podium_section.find_all('div', recursive=False)

                for div in podium_divs:
                    order_class = div.get('class', [])
                    order = None
                    if 'order-1' in order_class:
                        order = 2
                    elif 'order-2' in order_class:
                        order = 1
                    elif 'order-3' in order_class:
                        order = 3

                    if order:
                        driver_img = div.find('img', class_='f1-c-image')
                        driver_name = driver_img.get('alt') if driver_img else None
                        driver_src = driver_img.get('src') if driver_img else None
                        driver_code_tag = div.find('p', class_='f1-heading tracking-normal text-fs-14px leading-tight normal-case font-bold non-italic f1-heading__body font-formulaOne')
                        driver_code = driver_code_tag.get_text(strip=True) if driver_code_tag else None

                        podium.append({
                            'position': order,
                            'driver_name': driver_name,
                            'driver_code': driver_code,
                            'driver_image': driver_src
                        })

                if podium:
                    race_data['podium'] = sorted(podium, key=lambda x: x['position'])

            races_info.append(race_data)

        cached_races = races_info
        return races_info

    except Exception as e:
        print("[ERROR] Failed to fetch races:", e)
        traceback.print_exc()
        return []

def get_race_by_id(race_id):
    races = get_all_races()
    return next((r for r in races if r['race_id'] == race_id), None)

def search_races(query):
    races = get_all_races()
    results = []
    for race in races:
        if query in race.get('grand_prix_name', '').lower() or query in race.get('location', '').lower():
            results.append(race)
    return results

def get_all_race_urls():
    races = get_all_races()
    race_urls = [race['link'] for race in races if 'link' in race]
    return race_urls

def clear_cache():
    global cached_races
    cached_races = []
