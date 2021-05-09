from typing import List, Mapping
import json

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

covid_home_url_maps = [{
    "State":
    "Karnataka",
    "City":
    "Bengaluru",
    "URL":
    "https://covidbengaluru.com/data/covidbengaluru.com/bed_data.json"
}, {
    "State":
    "West Bengal",
    "City":
    None,
    "URL":
    "https://covidwb.com/data/covidwb.com/bed_data.json"
}, {
    "State":
    "Maharastra",
    "City":
    "Pune",
    "URL":
    "https://covidpune.com/data/covidpune.com/bed_data.json"
}, {
    "State":
    "Gujarat",
    "City":
    "Ahmedabad",
    "URL":
    "https://covidamd.com/data/covidamd.com/bed_data.json"
}, {
    "State":
    "Gujarat",
    "City":
    "Vadodara",
    "URL":
    "https://covidbaroda.com/data/covidbaroda.com/bed_data.json"
}, {
    "State":
    "Maharastra",
    "City":
    "Nashik",
    "URL":
    "https://covidnashik.com/data/covidnashik.com/bed_data.json"
}, {
    "State":
    "Maharastra",
    "City":
    "Beed",
    "URL":
    "https://covidbeed.com/data/covidbeed.com/bed_data.json"
}]


def map_raw_resource_str_to_type(resource_str: str) -> ResourceType:
    if resource_str.endswith("beds_allocated_to_covid"):
        return ResourceType.BEDS
    if resource_str.endswith("beds_without_oxygen"):
        return ResourceType.BED_WITHOUT_OXYGEN
    if resource_str.endswith("beds_with_oxygen"):
        return ResourceType.BED_WITH_OXYGEN
    if resource_str.endswith("icu_beds_with_ventilator"):
        return ResourceType.ICU_WITH_VENTILATOR
    if resource_str.endswith("icu_beds_without_ventilator"):
        return ResourceType.ICU_WITHOUT_VENTILATOR
    return None


def get_bed_resources(hosp_json):
    resources = {}
    for key in hosp_json:
        resource_type = map_raw_resource_str_to_type(key)
        if not resource_type:
            continue
        if resource_type not in resources:
            resources[resource_type] = Resource(resource_type, "", 0, 0)
        resource_obj = resources[resource_type]
        if key.startswith("total_"):
            resource_obj.total_qty = hosp_json[key]
        elif key.startswith("available_"):
            resource_obj.resource_qty = hosp_json[key]
        elif key.startswith("amc_") or key.startswith("private_"):
            pass
        else:
            raise AssertionError("Unexpected key: " + key + str(hosp_json))
    return list(resources.values())


def parse_hospital(data, state, city):
    resources = get_bed_resources(data)
    last_updated_secs = 0
    if 'last_updated_on' in data:
        last_updated_secs = data.get('last_updated_on') / 1000
    hospital = Hospital(
        data.get('hospital_name', ''),
        data.get('hospital_address', ''),
        data.get('district', ''),
        city,
        state,
        '',  #location
        datetime.fromtimestamp(last_updated_secs),
        resources)
    if "pincode" in data:
        hospital.pincode = data["pincode"]
    hospital.debug_text = json.dumps(data)
    return hospital


# List of web data sources
def get_data_from_web(state_filter, city_filter):
    home_response_dict = {}
    for covid_source in covid_home_url_maps:
        if state_filter and state_filter != covid_source['State']:
            continue
        if city_filter and city_filter != covid_source['City']:
            continue
        domain = re.search("\/\/covid[a-z]*\.",
                           covid_source["URL"]).group(0).strip("\/\.")
        print((domain, covid_source))
        home_response_dict[domain] = requests.get(covid_source["URL"]).text
    return home_response_dict


def get_bed_resource_type(keys):
    return [key for key in keys if 'available_' in key and "beds" in key]


def get_data(state_filter=None, city_filter=None) -> Mapping[str, List]:
    now = datetime.now()
    home_response_dict = get_data_from_web(state_filter, city_filter)
    source_data = {}
    for covid_source in covid_home_url_maps:
        state = covid_source["State"]
        city = covid_source["City"]
        domain = re.search("\/\/covid[a-z]*\.",
                           covid_source["URL"]).group(0).strip("\/\.")
        URL = covid_source["URL"]

        if domain not in home_response_dict:
            continue
        # Use requests to retrieve data from a given URL
        home_response = home_response_dict[domain]

        # Parse the whole HTML page using BeautifulSoup
        bed_data = BeautifulSoup(home_response, 'html.parser')
        bed_data = json.loads(bed_data.text)

        output = []

        for data in bed_data:
            hospital = parse_hospital(data, state, city)
            hospital.url = URL
            output.append(hospital)
        source_data[URL] = output
    return source_data


def main():
    TN_URL = 'https://covidtnadu.com/data/covidtnadu.com/bed_data.json'
    hospitals = get_data(state_filter="Tamil Nadu")
    print(len(hospitals[TN_URL]))
    for hospital in hospitals[TN_URL]:
        print(hospital.last_updated)


if __name__ == "__main__":
    main()
