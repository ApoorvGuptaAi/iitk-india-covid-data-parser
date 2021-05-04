import json
import time

from generic_hospital_parser import get_data as generic_hospital_get_data
from noida_up_parser import get_noida_hospitals
from ranchi_parser import get_ranchi_hospitals
from database_helper import upload_hospitals
from haryana_parser import get_haryana_hospitals
from bihar_parser import get_bihar_hospitals

_VERSION = 1


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
    else:
        url_hospitals_map = generic_hospital_get_data(state_filter=state_filter,
                                                      city_filter=city_filter)
    if not url_hospitals_map:
        raise AssertionError('Illegal filter: state={}, city={}'.format(
            state_filter, city_filter))
    outputs = []
    for url in url_hospitals_map:
        hospitals = url_hospitals_map[url]
        start = time.time()
        size = len(hospitals)
        upload_hospitals(hospitals, job_id)
        output = {
            "state": state_filter,
            "url": url,
            "size": size,
            "duration": time.time() - start
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
    #print(main({'state': 'Jharkhand', 'city': 'Ranchi'}))
    main({'state': 'Gujarat'})
