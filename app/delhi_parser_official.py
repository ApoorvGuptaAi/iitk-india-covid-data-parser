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

DELHI_RESOURCES_HOST = 'https://coronabeds.jantasamvad.org/covid-info.js'
DELHI_HOSPITALS_HOST = 'https://coronabeds.jantasamvad.org/covid-facilities.js'

BEDS = ['beds.html', 'oxygen-beds.html', 'all-covid-icu-beds.html']


def get_data_from_web(url):
    webpage = requests.get(url)
    return BeautifulSoup(webpage.text, 'html.parser')


def parse_hospitals_data(page_data):
    hospitals = json.loads(
        page_data.string[len("var gnctd_covid_facilities_data = "):-1])
    return hospitals


def parse_resources_data(page_data):
    resources = json.loads(page_data.string[len("var gnctd_covid_data = "):-1])
    return resources


def get_resource_enum(key):
    if key == 'beds':
        return ResourceType.BED_WITHOUT_OXYGEN
    elif key == "oxygen_beds":
        return ResourceType.BED_WITH_OXYGEN
    elif key == "covid_icu_beds":
        return ResourceType.ICUS
    else:
        return None


def parse_hospital_resources(resources_details):
    hospitals = {}
    for key, value in resources_details.items():
        resource_type = get_resource_enum(key)
        if resource_type == None:
            continue
        for hospital_name, details in value.items():
            if hospital_name == "All":
                continue
            if hospital_name not in hospitals:
                hospital = Hospital(hospital_name, "", "", "Delhi", "Delhi", "",
                                    None, [])
                hospitals[hospital_name] = hospital
            resource = Resource(resource_type, "beds", details['vacant'],
                                details['total'])
            hospitals[hospital_name].resources.append(resource)
            # Using the last updated details from the first resource
            if hospitals[
                    hospital_name].last_updated == None and 'last_updated_at' in details:
                hospitals[hospital_name].last_updated = parser.parse(
                    details['last_updated_at'] + "IST",
                    tzinfos=tzinfos,
                    dayfirst=True)
    return hospitals


def get_delhi_hospitals():
    hospitals_data = get_data_from_web(DELHI_HOSPITALS_HOST)
    hospital_details = parse_hospitals_data(hospitals_data)
    resources_data = get_data_from_web(DELHI_RESOURCES_HOST)
    resources_details = parse_resources_data(resources_data)
    hospital_resources = parse_hospital_resources(resources_details)
    # Update address
    for name, hospital in hospital_resources.items():
        if hospital.last_updated == None:
            hospital.last_updated = datetime.fromtimestamp(0)
        hospital.url = DELHI_RESOURCES_HOST
        if name in hospital_details:
            details = hospital_details[name]
            hospital_resources[name].address = details['address']
            # hospital_resources[name].phone_number = details['phone_number'] -> not yet supported
            hospital_resources[name].location = details['location']
    return {DELHI_RESOURCES_HOST: list(hospital_resources.values())}


def main():
    hospital_data = get_delhi_hospitals()
    print(len(hospital_data[DELHI_RESOURCES_HOST]))
    print(hospital_data[DELHI_RESOURCES_HOST][0])
    print(hospital_data[DELHI_RESOURCES_HOST][-1])
    #upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()
