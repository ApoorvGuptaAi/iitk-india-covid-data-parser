import requests
from bs4 import BeautifulSoup
import datetime
from dateutil import parser
import dateutil
import json
import re

from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

HARYANA_URL = 'https://coronaharyana.in'


def get_updated_timestamp(updated_text):
    return parser.parse(updated_text[len('Updated On: '):], dayfirst=True)


def parse_hospital(hospital_div, district):
    entry_div = hospital_div.find('div', {'class': 'entry-content'})
    headings = entry_div.find_all('h6')
    name = headings[0].string[len('Facility Name: '):].strip()
    address = headings[0].attrs['title']
    beds_div = entry_div.find('p')
    beds_text = ''
    if beds_div:
        beds_text = beds_div.text
    else:
        print(entry_div)
    meta_info_div = hospital_div.find_all('li')
    updated_at = meta_info_div[0].string
    location = meta_info_div[1].find('a').attrs['onclick']
    beds_text = beds_text.replace('Beds Over Utilized ', '-')
    numbers = re.findall('-?(?:\d+?)+', beds_text)
    resources = [
        Resource(ResourceType.BEDS, 'total_beds', int(numbers[0])),
        Resource(ResourceType.BED_WITHOUT_OXYGEN, 'isolation_beds',
                 int(numbers[1])),
        Resource(ResourceType.ICU_WITHOUT_VENTILATOR, 'icu_beds',
                 int(numbers[2])),
        Resource(ResourceType.ICU_WITH_VENTILATOR, 'ventilator',
                 int(numbers[3]))
    ]
    hospital = Hospital(name, address, district, '', 'Haryana', location,
                        get_updated_timestamp(updated_at), resources,
                        'HaryanaParser', HARYANA_URL)
    return hospital


def get_hospital_list(district_name, district_index):
    hospital_list = []
    district_url = 'https://coronaharyana.in/?city=' + str(district_index)
    district_response = requests.get(district_url)
    district_soup = BeautifulSoup(district_response.text, 'html.parser')
    hospitals_div = district_soup.find('div', {
        'id': 'tab0'
    }).find_all('div', {'class': 'community-post'})
    for hospital_div in hospitals_div:
        hospital_list.append(parse_hospital(hospital_div, district_name))
    return hospital_list


def get_haryana_hospitals():
    all_hospitals = []
    haryana_districts = {
        "Ambala": 1,
        "Bhiwani": 2,
        "Chandigarh": 24,
        "Charki Dadri": 3,
        "Faridabad": 4,
        "Fatehabad": 5,
        "Gurugram": 6,
        "Hisar": 7,
        "Jhajjar": 8,
        "Jind": 9,
        "Kaithal": 10,
        "Karnal": 11,
        "Kurukshetra": 12,
        "Mahendragarh": 13,
        "Nuh": 23,
        "Palwal": 15,
        "Panchkula": 16,
        "Panipat": 17,
        "Rewari": 18,
        "Rohtak": 19,
        "Sirsa": 20,
        "Sonipat": 21,
        "Yamunanagar": 22
    }
    for district in haryana_districts.items():
        district_hospitals = get_hospital_list(district[0], district[1])
        all_hospitals.extend(district_hospitals)
    return {HARYANA_URL: all_hospitals}


def main():
    hospital_data = get_haryana_hospitals()
    print(len(hospital_data))
    print(len(hospital_data[HARYANA_URL]))
    print(hospital_data[HARYANA_URL][0])
    #upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()
