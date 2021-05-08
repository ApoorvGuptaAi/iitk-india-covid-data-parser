import requests
import dateutil.parser
from bs4 import BeautifulSoup

from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

from dateutil import parser
from dateutil import tz

tzinfos = {"IST": tz.gettz('Asia/Kolkata')}

# List of web data sources
UTTARAKHAND_URL = 'https://covid19.uk.gov.in/bedssummary.aspx'


def parse_hospital_row(row_data):
    district = row_data.find('span', {'id': 'lblDistrictName'}).text
    hospitalName = row_data.find('span', {'id': 'lblhospitalName'}).text
    availableGenBeds = int(
        row_data.find('span', {
            'id': 'Lbloccupiedgenralbeds'
        }).text)
    totalGenBeds = int(row_data.find('span', {'id': 'lbltotGenralbeds'}).text)
    availableOxyBeds = int(
        row_data.find('span', {
            'id': 'lbloccupiedoxygenbeds'
        }).text)
    totalOxyBeds = int(row_data.find('span', {'id': 'lbltotoxygenbeds'}).text)
    availableICUBeds = int(
        row_data.find('span', {
            'id': 'lbloccupiedicubeds'
        }).text)
    totalICUBeds = int(row_data.find('span', {'id': 'lbltoticubeds'}).text)
    lastUpdatedAt = parser.parse(row_data.find('span', {
        'id': 'lbllastupdated'
    }).text + "IST",
                                 tzinfos=tzinfos,
                                 dayfirst=True)
    resources = [
        Resource(ResourceType.BED_WITHOUT_OXYGEN, "", availableGenBeds,
                 totalGenBeds),
        Resource(ResourceType.BED_WITH_OXYGEN, "", availableOxyBeds,
                 totalOxyBeds),
        Resource(ResourceType.ICUS, "", availableICUBeds, totalICUBeds),
    ]
    hospital = Hospital(hospitalName, "", district, "", "Uttarakhand", "",
                        lastUpdatedAt, resources, "", UTTARAKHAND_URL, 0)
    return hospital


def get_data_from_web():
    webpage = requests.get(UTTARAKHAND_URL)
    return BeautifulSoup(webpage.text, 'html.parser')


def parse_web_data(soup):
    table = soup.find('table', {'id': 'grdhospitalbeds'})
    hospital_rows = table.find('tbody').find_all('tr')
    hospitals = []
    for row_data in hospital_rows:
        hospital = parse_hospital_row(row_data)
        hospitals.append(hospital)
    return hospitals


def get_uttarakhand_hospitals():
    scraped_data = get_data_from_web()
    hospitals = parse_web_data(scraped_data)
    return {UTTARAKHAND_URL: hospitals}


def main():
    hospital_data = get_uttarakhand_hospitals()
    print(len(hospital_data[UTTARAKHAND_URL]))
    #upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()
