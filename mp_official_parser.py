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


#WIP - not able to see total capacity from the webpage but avaialble in excel
MP_URL = 'http://sarthak.nhmmp.gov.in/covid/facility-bed-occupancy-details/?show=2000'


def get_data_from_web(url):
  webpage = requests.get(url)
  return BeautifulSoup(webpage.text, 'html.parser')

def parse_hospital_row(row_data):
  # only keep the english name
  hospital_name_raw = row_data.find('div', {'class' : 'hospitalname'}).text
  hospital_name = hospital_name_raw[:hospital_name_raw.index("/")]
  location = row_data.find('div', {'class' : 'hospitaladdrress'}).find('a')['href']
  bed_data = row_data.find('div', {'class' : 'deecriptions'})
  labels = bed_data.find_all('label')
  resources = [Resource(ResourceType.BED_WITHOUT_OXYGEN, "", labels[0].text, None),
               Resource(ResourceType.BED_WITH_OXYGEN, "", labels[1].text, None),
               Resource(ResourceType.ICUS, "", labels[2].text, None)]
  last_updated_at = datetime.fromtimestamp(0)
  try:
    last_updated_at = parser.parse(row_data.find('div', {'class' : 'last-updated'}).find('span').text.strip() + "IST", tzinfos=tzinfos)
  except Exception:
    print('Missing last updated info: ' + hospital_name)
  return Hospital(hospital_name, "", "", "", "Madhya Pradesh", location, last_updated_at, resources, "", MP_URL)

def parse_web_data(soup):
  table = soup.find('table', {'class': 'hospital-status'})
  hospital_rows = table.find('tbody').find_all('tr')
  hospitals = []
  row_id = 0
  # Even rows have availability and odd rows have hospital phone number details that can be parsed later
  for row_data in hospital_rows:
    # Skip odd rows
    if (row_id %2 == 1):
      row_id += 1
      continue
    # Parse even rows
    hospital = parse_hospital_row(row_data)
    hospitals.append(hospital)
    # print(hospital)
    row_id += 1
  return hospitals

def get_mp_hospitals():
  scraped_data = get_data_from_web(MP_URL)
  hospitals = parse_web_data(scraped_data)
  return { MP_URL : hospitals }

def main():
  hospital_list = get_mp_hospitals()
  print(len(hospital_list[MP_URL]))


if __name__ == "__main__":
    main()
