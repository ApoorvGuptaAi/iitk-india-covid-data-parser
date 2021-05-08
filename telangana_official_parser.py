import requests
import dateutil.parser
import json
from bs4 import BeautifulSoup
from datetime import datetime

from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

from dateutil import parser

TELANGANA_URL = 'http://164.100.112.24/SpringMVC/getHospital_Beds_Status_Citizen.htm'
post_params = ['G', 'P']

def get_data_from_web(url, postParams):
  webpage = requests.post(url, data = postParams)
  return BeautifulSoup(webpage.text, 'html.parser')

def get_district_post_params(scraped_data):
  district_map = {}
  districts_table = scraped_data.find('table', {'id': 'dataTable'})
  for row in districts_table.find('tbody').find_all('tr'):
    onclickjs = row.find('a')['onclick'][len('setState('):-1]
    params = onclickjs.split(',')[-1][1:-1]
    output = {x.split('=')[0]:int(x.split('=')[1]) for x in params.split("&")}
    district_name = row.find('a').text
    district_map[district_name] = output
  return district_map

def parse_row(district_name, columns):
  # 0 Name
  # 1 Phone number
  # Total Occupied Vacant
  # 2 3 4 Regular Beds
  # 5 6 7 Oxygen Beds
  # 8 9 10 ICU Beds
  # 11 12 13 (Sum of above 2 categories)
  # 14 15 Last updated (date and time)
  # print(row_data.text)
  resources = [
               Resource(ResourceType.BED_WITHOUT_OXYGEN, int(columns[4].text), int(columns[2].text)),
               Resource(ResourceType.BED_WITH_OXYGEN, int(columns[7].text), int(columns[5].text)),
               Resource(ResourceType.ICUS, int(columns[10].text), int(columns[8].text))
  ]
  prefixed_name = columns[0].text
  hospital_name = prefixed_name[prefixed_name.find('.')+2:]
  return Hospital(hospital_name, "", district_name, "", "Telangana", "", 
                  parser.parse(columns[14].text + " " + columns[15].text + " +05:30", dayfirst=True), 
                  resources, "", TELANGANA_URL)

def parse_data_from_web(raw_data):
  hospitals = []
  rows = raw_data.find('table', {'id': 'datatable-default1'}).find('tbody').find_all('tr')
  current_district = ""
  for row in rows:
    columns = row.find_all('td')
    if (len(columns)) == 18:
      current_district = columns[1].text
      hospitals.append(parse_row(current_district, columns[2:]))
    else:
      hospitals.append(parse_row(current_district, columns))
  return hospitals

def get_telangana_hospitals():
  hospitals = []
  for param in post_params:
    hospital_type_data = get_data_from_web(TELANGANA_URL, {'hospital': param})
    type_hospitals = parse_data_from_web(hospital_type_data)
    print(param + str(len(type_hospitals)))
    hospitals.extend(type_hospitals)
  return {TELANGANA_URL : hospitals}

def main():
  hospitals = get_telangana_hospitals()
  print(len(hospitals[TELANGANA_URL]))
  print(hospitals[TELANGANA_URL][0])
  print(hospitals[TELANGANA_URL][-1])
  return 

if __name__ == "__main__":
    main()