import requests
import dateutil.parser
import json
from bs4 import BeautifulSoup
from datetime import datetime

from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

from dateutil import parser
from dateutil import tz

tzinfos = {"IST": tz.gettz('Asia/Kolkata')}

LUDHIANA_URL = "http://hbmsludhiana.in/index_app_detail.php?type=all"


def get_data_from_web(url):
    webpage = requests.get(url)
    return BeautifulSoup(webpage.text, 'html.parser')


def parse_hospital_row(data):
    hospital_name = data.find('p', {'class': 'mb-0'}).string
    # Phone number not supported yet
    # phone_num = data.find('p', {'class' : 'm1-1'}).string
    last_updated_at = data.find('small', {
        'class': 'text-muted'
    }).text[len("Update On : "):]
    resource_rows = data.find('table').find('tbody').find_all('tr')

    icu_ventilator = resource_rows[0].find_all('td')
    icu_wo_ventilator = resource_rows[1].find_all('td')
    bed_oxy = resource_rows[2].find_all('td')
    bed_wo_oxy = resource_rows[3].find_all('td')
    resources = [
        Resource(ResourceType.BED_WITHOUT_OXYGEN, "", int(bed_wo_oxy[2].text),
                 int(bed_wo_oxy[1].text)),
        Resource(ResourceType.BED_WITH_OXYGEN, "", int(bed_oxy[2].text),
                 int(bed_oxy[1].text)),
        Resource(ResourceType.ICU_WITH_VENTILATOR, "",
                 int(icu_ventilator[2].text), int(icu_ventilator[1].text)),
        Resource(ResourceType.ICU_WITHOUT_VENTILATOR, "",
                 int(icu_wo_ventilator[2].text), int(icu_wo_ventilator[1].text))
    ]
    return Hospital(hospital_name, "", "", "Ludhiana", "Punjab", "",
                    parser.parse(last_updated_at + "+05:30", dayfirst=True),
                    resources, "", LUDHIANA_URL)


def parse_web_data(soup):
    hospitals = []
    hospitals_data = soup.find('div', {
        'class': 'card-body'
    }).find_all('div', {'class': 'py-2'})
    for data in hospitals_data:
        hospitals.append(parse_hospital_row(data))
    return hospitals


def get_ludhiana_hospitals():
    scraped_data = get_data_from_web(LUDHIANA_URL)
    hospitals = parse_web_data(scraped_data)
    return {LUDHIANA_URL: hospitals}


def main():
    hospital_list = get_ludhiana_hospitals()
    print(len(hospital_list[LUDHIANA_URL]))
    print(hospital_list[LUDHIANA_URL][0])
    print(hospital_list[LUDHIANA_URL][-1])


if __name__ == "__main__":
    main()
