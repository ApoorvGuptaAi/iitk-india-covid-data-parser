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


# Gujarat - Surat
SURAT_URL = 'http://office.suratsmartcity.com/SuratCOVID19/Home/COVID19BedAvailabilitydetails'

def get_data_from_web(url):
  webpage = requests.get(url)
  return BeautifulSoup(webpage.text, 'html.parser')

def parse_hospital_row(data):
  availability = data.find_all('div', {'class' : 'count-text'})
  total_resources = data.find_all('span', {'class' : 'count-text'})
  resources = [
               Resource(ResourceType.BEDS, "", int(total_resources[1].text[len('Total Vacant - '):]), int(total_resources[0].text[len('Total Beds - '):])),
               Resource(ResourceType.BED_WITHOUT_OXYGEN, "", int(availability[0].text), None),
               Resource(ResourceType.BED_WITH_OXYGEN, "", int(availability[1].text), None),
               Resource(ResourceType.ICU_WITHOUT_VENTILATOR, "", int(availability[2].text), None),
               Resource(ResourceType.ICU_WITH_VENTILATOR, "", int(availability[3].text), None)
  ]
  last_updated_at = data.find('span', {'class' : 'badge-lastupdated'}).string[len("Last Updated- "):]
  hospital_name = data.find('a', {'class' : 'hospital-info'})['href'][len("javascript:showpopup("):-2].split(',')[0][1:-1]#data.find('a', {'class' : 'hospital-info'}).text
  hospital_address = data.find('a', {'class' : 'hospital-info'})['href'][len("javascript:showpopup("):-2].split(',')[1][1:-1]
  # phone_numer not yet supported
  # phone_number = data.find('a', {'class' : 'hospital-info'})['href'][len("javascript:showpopup("):-2].split(',')[2][1:-1]
  return Hospital(hospital_name, hospital_address, "", "Surat", "Madhya Pradesh", "", parser.parse(last_updated_at+ "+05:30"), resources, "", SURAT_URL)

def parse_web_data(soup):
  hospitals = []
  hospitals_data = soup.find('section', {'class' : 'COVID19BedAvailability'}).find_all('div', {'class': 'custom-card'})
  for data in hospitals_data:
    hospitals.append(parse_hospital_row(data))
  return hospitals

def get_surat_hospitals():
  scraped_data = get_data_from_web(SURAT_URL)
  hospitals = parse_web_data(scraped_data)
  return { SURAT_URL : hospitals }

def main():
  hospital_list = get_surat_hospitals()
  print(len(hospital_list[SURAT_URL]))
  print(hospital_list[SURAT_URL][0])
  print(hospital_list[SURAT_URL][-1])

if __name__ == "__main__":
    main()

