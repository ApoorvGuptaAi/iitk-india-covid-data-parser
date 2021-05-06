from bs4 import BeautifulSoup
import requests
from hospital import Hospital, Resource, ResourceType
from datetime import datetime
from database_helper import upload_hospitals

PUDUCHERRY_URL = 'https://covid19dashboard.py.gov.in/BedAvailabilityDetails'
COL_NAMES = [
    'hosp_name', 'last_updated', 'no_oxygen_alloted', 'no_oxygen_vacant', 'oxygen_alloted', 'oxygen_vacant', 'icu_ventilator_alloted', 'icu_ventilator_vacant'
]


def get_puducherry_hospitals():
    hospital_data = []
    page = requests.get(PUDUCHERRY_URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find('table')
    for row in tables.find_all('tr'):
        row_data = [d.text.strip() for d in row.find_all('td')]
        if not row_data or len(row_data) != len(COL_NAMES):
            continue
        row_data = {c: r for r, c in zip(row_data, COL_NAMES)}
        last_updated = datetime.strptime(row_data['last_updated'],
                                         '%d-%m-%Y %H:%M:%S')
        resources = [
            Resource(ResourceType.BED_WITHOUT_OXYGEN, None,
                     int(row_data['no_oxygen_vacant']),
                     int(row_data['no_oxygen_alloted'])),
            Resource(ResourceType.BED_WITH_OXYGEN, None,
                     int(row_data['oxygen_vacant']),
                     int(row_data['oxygen_alloted'])),
            Resource(ResourceType.ICU_WITH_VENTILATOR, None, int(row_data['icu_ventilator_vacant']),
                     int(row_data['icu_ventilator_alloted']))
        ]
        hosp = Hospital(row_data['hosp_name'], None, 'Puducherry', 'Puducherry',
                        'Puducherry', '', last_updated, resources)
        hosp.url = PUDUCHERRY_URL
        hosp.debug_text = str(row_data)
        hospital_data.append(hosp)
    return {PUDUCHERRY_URL: hospital_data}