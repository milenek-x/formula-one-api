import requests
from bs4 import BeautifulSoup
from races import get_all_race_urls

cached_sessions = []

def get_race_sessions(race_url):
    global cached_sessions
    if cached_sessions:
        return cached_sessions

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(race_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    session_blocks1 = soup.find_all('div', class_='relative px-xs py-s tablet:p-normal tablet:pl-0 tablet:pr-normal rounded-md flex flex-wrap tablet:flex-nowrap mt-micro items-center bg-white')
    session_blocks2 = soup.find_all('div', class_='relative px-xs py-s tablet:p-normal tablet:pl-0 tablet:pr-normal rounded-md flex flex-wrap tablet:flex-nowrap mt-micro items-center bg-white pr-l')

    all_sessions = session_blocks1 + [b for b in session_blocks2 if b not in session_blocks1]

    session_list = []
    for session in all_sessions:
        name = session.find('span', class_='f1-heading tracking-normal text-fs-18px leading-tight normal-case font-bold non-italic f1-heading__body font-formulaOne block mb-xxs')
        date = session.find('p', class_='f1-heading tracking-normal text-fs-18px leading-none normal-case font-normal non-italic f1-heading__body font-formulaOne')
        month = session.find('span', class_='f1-heading tracking-normal text-fs-12px leading-tight uppercase font-normal non-italic f1-heading__body font-formulaOne')
        time = session.find('p', class_='f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-none f1-text__micro text-fs-15px')

        start_time = end_time = None
        if time and time.find('span'):
            raw_time = time.find('span').text.strip()
            if '-' in raw_time:
                start_time, end_time = [t.strip() for t in raw_time.split('-')]
            else:
                start_time = raw_time

        session_list.append({
            'name': name.get_text(strip=True) if name else None,
            'date': date.get_text(strip=True) if date else None,
            'month': month.get_text(strip=True) if month else None,
            'start_time': start_time,
            'end_time': end_time
        })

    return session_list

def clear_cache():
    global cached_sessions
    cached_sessions = []
