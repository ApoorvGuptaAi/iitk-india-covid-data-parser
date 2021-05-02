import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import datetime
from dataclasses import dataclass
import dateutil
import re

@dataclass
class Hospital:
  name: str
  address: str
  district: str
  state: str
  beds_text: str
  location: str
  total_beds: int
  isolation_beds: int
  icu_beds: int
  ventilator: int
  last_updated: datetime.datetime
    
class PersonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Hospital):
            return obj.__dict__
        # Base class default() raises TypeError:
        return json.JSONEncoder.default(self, obj)

def get_updated_timestamp(updated_text):
  return dateutil.parser.parse(updated_text[len('Updated On: '):])

def parse_hospital(hospital_div, district):
  entry_div = hospital_div.find('div', {'class' : 'entry-content'})
  headings = entry_div.find_all('h6')
  name = headings[0].string
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
  hospital = Hospital(name, address, district, 'Haryana', beds_text, location, 0, 0, 0, 0, get_updated_timestamp(updated_at))
  hospital.name = hospital.name[len('Facility Name: '):].strip()
  hospital.beds_text = hospital.beds_text.replace('Beds Over Utilized ', '-')
  numbers = re.findall('-?(?:\d+,?)+', hospital.beds_text)
  hospital.total_beds = numbers[0]
  hospital.isolation_beds = numbers[1]
  hospital.icu_beds = numbers[2]
  hospital.ventilator = numbers[3]
  return hospital

def get_hospital_list(district_name, district_index):
  hospital_list = []
  district_url = 'https://coronaharyana.in/?city=' + str(district_index)
  district_response = requests.get(district_url)
  district_soup = BeautifulSoup(district_response.text, 'html.parser')
  hospitals_div = district_soup.find('div', {'id': 'tab0'}).find_all('div', {'class': 'community-post'})
  for hospital_div in hospitals_div:
    hospital_list.append(parse_hospital(hospital_div, district_name))
  return hospital_list

def get_haryana_hospitals():
  all_hospitals = []
  haryana_districts = {"Ambala":1,"Bhiwani":2,"Chandigarh":24,"Charki Dadri":3,"Faridabad":4,"Fatehabad":5,"Gurugram":6,"Hisar":7,"Jhajjar":8,"Jind":9,"Kaithal":10,"Karnal":11,"Kurukshetra":12,"Mahendragarh":13,"Nuh":23,"Palwal":15,"Panchkula":16,"Panipat":17,"Rewari":18,"Rohtak":19,"Sirsa":20,"Sonipat":21,"Yamunanagar":22}
  for district in haryana_districts.items():
    district_hospitals = get_hospital_list(district[0], district[1])
    all_hospitals.extend(district_hospitals)
    break
  return all_hospitals


def lambda_handler(event, context):
    print('debug')
    all_hospitals = get_haryana_hospitals()
    # TODO implement
    return json.dumps({})
