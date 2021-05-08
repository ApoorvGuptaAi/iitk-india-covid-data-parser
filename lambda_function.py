from typing import List
import json
import time

from bihar_parser import get_bihar_hospitals
from maharashtra_navi_mumbai_parser import get_hospital_data as get_maharashtra_navi_mumbai_data
from database_helper import upload_hospitals, resource_to_json
from generic_hospital_parser import get_data as generic_hospital_get_data
from haryana_parser import get_haryana_hospitals
from hospital import Resource, Hospital
from noida_up_parser import get_noida_hospitals
from rajasthan_parser import get_rajasthan_hospitals
from ranchi_parser import get_ranchi_hospitals
from uttarakhand_parser import get_uttarakhand_hospitals
from gujarat_gandhinagar_parser import get_data as get_gujarat_gandhinagar_data
from delhi_parser_official import get_delhi_hospitals
from puducherry_parser import get_puducherry_hospitals
from thane_parser import get_thane_hospitals
from gujarat_surat_parser import get_surat_hospitals
from punjab_ludhiana_parser import get_ludhiana_hospitals
from tn_official_parser import get_tn_hospitals

_VERSION = 1


def summarize_resources(hospitals: List[Hospital]):
    resources = {}
    for hospital in hospitals:
        for resource in hospital.resources:
            r_type = resource.resource_type
            if r_type not in resources:
                resources[r_type] = Resource(r_type, '', 0, 0)
            summary = resources[r_type]
            if resource.total_qty != None:
              summary.total_qty += resource.total_qty
            if resource.resource_qty != None:
              summary.resource_qty += resource.resource_qty
    return {k: resource_to_json(v) for (k, v) in resources.items()}


def main(request):
    state_filter = request.get('state', None) if request else None
    city_filter = request.get('city', None) if request else None
    print("Filters: {}, {}".format(state_filter, city_filter))
    job_id = "Parser{}-{}-{}-{}".format(_VERSION, round(time.time()),
                                        state_filter, city_filter)
    print("JOBID: ", job_id)
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
    elif state_filter == "Rajasthan":
        url_hospitals_map = get_rajasthan_hospitals()
    elif state_filter == "Maharashtra" and city_filter == "Navi Mumbai":
        url_hospitals_map = get_maharashtra_navi_mumbai_data()
    elif state_filter == "Gujarat" and city_filter == "Gandhinagar":
        url_hospitals_map = get_gujarat_gandhinagar_data()
    elif state_filter == "Delhi":
        url_hospitals_map = get_delhi_hospitals()
    elif state_filter == "Puducherry":
        url_hospitals_map = get_puducherry_hospitals()
    elif state_filter == "Maharashtra" and city_filter == "Thane":
        url_hospitals_map = get_thane_hospitals()
    elif state_filter == "Gujarat" and city_filter == "Surat":
        url_hospitals_map = get_surat_hospitals()
    elif state_filter == "Punjab" and city_filter == "Ludhiana":
        url_hospitals_map = get_ludhiana_hospitals()
    elif state_filter == "Tamil Nadu":
        url_hospitals_map = get_tn_hospitals()
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
    output_str = json.dumps({"outputs": outputs})
    print(output_str)
    return output_str


def lambda_handler(event, context):
    if not event['state']:
        raise AssertionError(
            "Please specify state in request, Otherwise lambda will timeout. " +
            json.dumps(event))
    return main(event)


if __name__ == "__main__":
    # print(main({'state': 'Jharkhand', 'city': 'Ranchi'}))
    # print(main({'state': 'Rajasthan'}))
    # print(main({'state': 'Maharashtra', 'city': 'Navi Mumbai'}))
    # print(main({'state': 'Haryana'}))
    # print(main({'state': 'UP', 'city': 'Noida'}))
    # print(main({'state': 'Gujarat', 'city': 'Gandhinagar'}))
    # main({'state' : 'Delhi'})
    # print(main({'state': 'Gujarat', 'city': 'Surat'}))
    print(main({'state': 'Punjab', 'city': 'Ludhiana'}))
    # print(main({'state': 'Tamil Nadu'}))
