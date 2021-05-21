import requests
import dateutil.parser
import json
from bs4 import BeautifulSoup
from datetime import datetime

from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

from dateutil import parser
from dateutil import tz

AP_URL = "http://dashboard.covid19.ap.gov.in/ims/hospbed_reports/process.php"

def get_data_from_web(url, postParams):
  webpage = requests.post(url, data = postParams)
  return BeautifulSoup(webpage.text, 'html.parser')

def get_district_post_params(scraped_data):
  district_map = {}
  districts_table = scraped_data.find('table', {'id': 'dataTable'})
  for row in districts_table.find('tbody').find_all('tr'):
    onclickjs = row.find('a')['onclick'][len('setState('):-1]
    params = onclickjs.split(',')[-1][1:-1]
    output = {x.split('=')[0]:x.split('=')[1] for x in params.split("&")}
    district_name = row.find('a').text
    district_map[district_name] = output
  return district_map

def parse_row(district, row_data):
  # print(row_data.text)
  columns = row_data.find_all('td')
  # 0 Number
  # 1 Name
  # 2 Phone number
  # 3 Nodal officer number
  # 4 Govt/Pvt
  # Total occupied available
  # 5 6 7 ICU Beds
  # 8 9 10 O2 General Beds
  # 11 12 13 General Beds
  # 14 15 16 number of Ventilator but not known if avilable or not
  resources = [
    Resource(ResourceType.BED_WITHOUT_OXYGEN, "", int(columns[13].text), int(columns[11].text)),
    Resource(ResourceType.BED_WITH_OXYGEN, "", int(columns[10].text), int(columns[8].text)),
    Resource(ResourceType.ICUS, "", int(columns[7].text), int(columns[5].text)),
    Resource(ResourceType.ICU_WITH_VENTILATOR, "", int(columns[16].text), int(columns[14].text))
  ]
  return Hospital(columns[1].text, "", district, "", "Andhra Pradesh", "", datetime.fromtimestamp(0), resources, "", AP_URL)

def parse_data_from_web(district, raw_data):
  hospitals = []
  # Parsing raw data from district website
  rows = raw_data.find('table', {'id': 'dataTable'}).find('tbody').find_all('tr')
  for row in rows:
    hospitals.append(parse_row(district, row))
  return hospitals

def get_ap_hospitals():
  scraped_data = get_data_from_web(AP_URL, {'districtGraph': 1})
  district_map = get_district_post_params(scraped_data)
  hospitals = []
  for key, value in district_map.items():
    district_scraped_data = get_data_from_web(AP_URL, value)
    district_hospitals = parse_data_from_web(key, district_scraped_data)
    print(key + str(len(district_hospitals)))
    hospitals.extend(district_hospitals)
  return {AP_URL : hospitals}

def main():
  hospitals = get_ap_hospitals()
  print(len(hospitals[AP_URL]))
  print(hospitals[AP_URL][0])
  print(hospitals[AP_URL][53])
  print(hospitals[AP_URL][-1])  
  return 


if __name__ == "__main__":
    main()