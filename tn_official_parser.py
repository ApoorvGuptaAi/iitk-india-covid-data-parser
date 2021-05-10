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

#Tamil Nadu
TN_URL = "https://stopcorona.tn.gov.in/beds.php"


def get_data_from_web(url):
    webpage = requests.get(url)
    return BeautifulSoup(webpage.text, 'html.parser')


def parse_hospital_row(row_data):
    # print(row_data)
    columns = row_data.find_all('td')
    # 0,1 District, HospitalName,
    # 2,3,4 CovidBeds (total, occupied, vacant),
    # 5,6,7 Oxy (total, occupied, vacant),
    # 8,9,10 Non-oxy(total, occupied, vacant),
    # 11,12,13 ICU (total, occupied, vacant),
    # 14,15,16 ventilators (total, occupied, vacant),
    # 17 Last updated,
    # 18 Contact number,
    # 19 Misc
    resources = [
        Resource(ResourceType.BEDS, "covid_beds", int(columns[4].text),
                 int(columns[2].text)),
        Resource(ResourceType.BED_WITH_OXYGEN, "", int(columns[7].text),
                 int(columns[5].text)),
        Resource(ResourceType.BED_WITHOUT_OXYGEN, "", int(columns[10].text),
                 int(columns[8].text)),
        Resource(ResourceType.ICU_WITHOUT_VENTILATOR, "", int(columns[13].text),
                 int(columns[11].text)),
        Resource(ResourceType.ICU_WITH_VENTILATOR, "", int(columns[16].text),
                 int(columns[14].text)),
    ]
    # Data is not in day first order.
    return Hospital(columns[1].text, "", columns[0].text, "", "Tamil Nadu", "",
                    parser.parse(columns[17].text + "+05:30"),
                    resources, "", TN_URL)


def parse_web_data(soup):
    hospitals = []
    hospitals_data = soup.find('table', {
        'id': 'dtBasicExample'
    }).find('tbody').find_all('tr')
    print(len(hospitals_data))
    for data in hospitals_data:
        hospitals.append(parse_hospital_row(data))
    return hospitals


def get_tn_hospitals():
    scraped_data = get_data_from_web(TN_URL)
    hospitals = parse_web_data(scraped_data)
    return {TN_URL: hospitals}


def main():
    hospital_list = get_tn_hospitals()
    print(len(hospital_list[TN_URL]))
    print(hospital_list[TN_URL][0])
    print(hospital_list[TN_URL][-1])


if __name__ == "__main__":
    main()
