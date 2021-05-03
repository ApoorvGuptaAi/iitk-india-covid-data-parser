import json

from generic_hospital_parser import get_data as generic_hospital_get_data
from database_helper import upload_hospitals


def main(request={}):
    state_filter = request['state'] if request else None
    city_filter = None
    # Add if-else based on state and city.
    url_hospitals_map = generic_hospital_get_data(state_filter=state_filter,
                                                  city_filter=city_filter)
    output = []
    for url in url_hospitals_map:
        hospitals = url_hospitals_map[url]
        size = len(hospitals)
        upload_hospitals(hospitals)
        output.append({"state": state_filter, "url": url, "size": size})
    return json.dumps(output)


def lambda_handler(event, context):
    return json.dumps(main())


if __name__ == "__main__":
    print(main({'state': 'Gujarat'}))
