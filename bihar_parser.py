import requests

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

# List of web data sources
BIHAR_URL = 'https://covid19health.bihar.gov.in/DailyDashboard/BedsOccupied'


def get_data_from_web(web_url):
    response = requests.get(web_url)
    return BeautifulSoup(response.text, 'html.parser')


def get_updated_timestamp(updated_text):
    if updated_text:
        return parser.parse(updated_text)


def parse_hospital_data(hospital_tds):
    parsed_data = {
        'district': hospital_tds[0].find('span', {
            'class': 'bed-district'
        }).text,
        'name': hospital_tds[1].find('span', {
            'class': 'bed-title'
        }).text,
        'map_href': hospital_tds[1].find('a')['href'],
        'category': hospital_tds[2].text,
        'last_updated': get_updated_timestamp(hospital_tds[3].text),
        'total_beds': hospital_tds[4].text,
        'vacant_beds': hospital_tds[5].text,
        'icu_beds': hospital_tds[6].text,
        'vacant_icu_beds': hospital_tds[7].text,
        'contact_phone': hospital_tds[8].text,
    }
    return parsed_data


def get_bihar_data(bihar_soup):
    master_table = bihar_soup.find('table', {'id': 'example'})
    hospital_rows = master_table.find_all('tr')
    all_hospitals = []
    for hospital_row in hospital_rows[1:]:
        hospital_tds = hospital_row.find_all('td')
        hospital_data = parse_hospital_data(hospital_tds)
        resources = [
            Resource(resource_type=ResourceType.BEDS,
                     resource_description='hospital beds',
                     resource_qty=hospital_data['vacant_beds'],
                     total_qty=hospital_data['total_beds']),
            Resource(resource_type=ResourceType.ICUS,
                     resource_description='icu beds',
                     resource_qty=hospital_data['vacant_icu_beds'],
                     total_qty=hospital_data['icu_beds']),
        ]
        hospital = Hospital('', '', '', '', '', '', datetime.now(), resources)
        hospital.name = hospital_data['name']
        hospital.district = hospital_data['district']
        hospital.state = 'BIHAR'
        hospital.location = hospital_data['map_href']
        hospital.last_updated = hospital_data['last_updated']
        hospital.debug_text = str(hospital_tds)
        if not hospital.last_updated:
            print("Skipping hospital {}-{} due to missing timestamp",
                  hospital.name, hospital.district)
            continue
        hospital.url = BIHAR_URL
        all_hospitals.append(hospital)
    return all_hospitals


def get_bihar_hospitals():
    scraped_data = get_data_from_web(web_url=BIHAR_URL)
    all_hospitals = get_bihar_data(scraped_data)
    return {BIHAR_URL: all_hospitals}


def main():
    hospital_data = get_bihar_hospitals()
    # upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()