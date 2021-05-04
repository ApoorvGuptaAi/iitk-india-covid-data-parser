from typing import List
import json
import time

from hospital import Resource, Hospital
from database_helper import upload_hospitals, resource_to_json
from generic_hospital_parser import get_data as generic_hospital_get_data
from noida_up_parser import get_noida_hospitals
from ranchi_parser import get_ranchi_hospitals
from haryana_parser import get_haryana_hospitals
from bihar_parser import get_bihar_hospitals
from uttarakhand_parser import get_uttarakhand_hospitals

_VERSION = 1


def summarize_resources(hospitals: List[Hospital]):
    resources = {}
    for hospital in hospitals:
        for resource in hospital.resources:
            r_type = resource.resource_type
            if r_type not in resources:
                resources[r_type] = Resource(r_type, '', 0, 0)
            summary = resources[r_type]
            summary.total_qty += resource.total_qty
            summary.resource_qty += resource.resource_qty
    return {k: resource_to_json(v) for (k, v) in resources.items()}


def main(request):
    state_filter = request.get('state', None) if request else None
    city_filter = request.get('city', None) if request else None
    print("Filters: {}, {}".format(state_filter, city_filter))
    job_id = "Parser{}-{}-{}-{}".format(_VERSION, round(time.time()),
                                        state_filter, city_filter)
    # Add if-else based on state and city.
    if state_filter == "UP" and city_filter == "Noida":
        url_hospitals_map = get_noida_hospitals()
    elif state_filter == "Jharkhand" and city_filter == "Ranchi":
        url_hospitals_map = get_ranchi_hospitals()
    elif state_filter == "Haryana":
        url_hospitals_map = get_haryana_hospitals()
    elif state_filter == "Bihar":
        url_hospitals_map = get_bihar_hospitals()
    elif state_filter == "Uttarakhand":
        url_hospitals_map = get_uttarakhand_hospitals()
    else:
        url_hospitals_map = generic_hospital_get_data(state_filter=state_filter,
                                                      city_filter=city_filter)
    if not url_hospitals_map:
        raise AssertionError('Illegal filter: state={}, city={}'.format(
            state_filter, city_filter))
    outputs = []
    for url in url_hospitals_map:
        hospitals = url_hospitals_map[url]
        resources_summary = summarize_resources(hospitals)
        start = time.time()
        size = len(hospitals)
        upload_hospitals(hospitals, job_id)
        output = {
            "state": state_filter,
            "url": url,
            "size": size,
            "duration": time.time() - start,
            "resources": list(resources_summary.values())
        }
        if city_filter:
            output["city"] = city_filter
        outputs.append(output)
    output_str = json.dumps({"outputs": outputs}, indent=2)
    print(output_str)
    return output_str


def lambda_handler(event, context):
    if not event['state']:
        raise AssertionError(
            "Please specify state in request, Otherwise lambda will timeout. " +
            json.dumps(event))
    return main(event)


if __name__ == "__main__":
    #print(main({'state': 'Jharkhand', 'city': 'Ranchi'}))
    print(main({'state': 'Uttarakhand'}))
