from typing import List, Mapping
import json

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

from hospital import Hospital, Resource, map_raw_resource_str_to_type
from database_helper import upload_hospitals

covid_home_url_maps = [{
    "State":
    "Delhi",
    "City":
    "Delhi",
    "URL":
    "https://coviddelhi.com/data/coviddelhi.com/bed_data.json"
}, {
    "State":
    "Karnataka",
    "City":
    "Bengaluru",
    "URL":
    "https://covidbengaluru.com/data/covidbengaluru.com/bed_data.json"
}, {
    "State":
    "Andhra Pradesh",
    "City":
    None,
    "URL":
    "https://covidaps.com/data/covidaps.com/bed_data.json"
}, {
    "State":
    "Telengana",
    "City":
    None,
    "URL":
    "https://covidtelangana.com/data/covidtelangana.com/bed_data.json"
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
    "Madhya Pradesh",
    "City":
    None,
    "URL":
    "https://covidmp.com/data/covidmp.com/bed_data.json"
}, {
    "State":
    "Tamil Nadu",
    "City":
    None,
    "URL":
    "https://covidtnadu.com/data/covidtnadu.com/bed_data.json"
}, {
    "State":
    "Maharastra",
    "City":
    "Beed",
    "URL":
    "https://covidbeed.com/data/covidbeed.com/bed_data.json"
}, {
    "State":
    "Gujarat",
    "City":
    "Gandhi Nagar",
    "URL":
    "https://covidgandhinagar.com/data/covidgandhinagar.com/bed_data.json"
}]


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
            resources = []
            empty_resources = 0
            non_empty_resources = 0
            for resource in get_bed_resource_type(data.keys()):
                if data[resource] == 0:
                    empty_resources += 1
                else:
                    non_empty_resources += 1
                resource_type = map_raw_resource_str_to_type(resource)
                assert resource_type
                resources.append(
                    Resource(resource_type, resource, data[resource]))
            hospital = Hospital(
                data.get('hospital_name', ''),
                data.get('hospital_address', ''),
                data.get('district', ''),
                city,
                state,
                '',  #location
                datetime.fromtimestamp(
                    data.get('last_updated_on', now.timestamp()) / 1000),
                resources)
            hospital.url = URL
            hospital.debug_text = json.dumps(data)
            output.append(hospital)
        source_data[URL] = output
    return source_data


def main():
    data = get_output_from_data()
    for url in data:
        upload_hospitals(data[url])


if __name__ == "__main__":
    main()
