import os
import requests

from hospital import Hospital
from hospital import Resource


#https://www.getpostman.com/collections/ac744d6c750be50db61e
def resource_to_json(resource: Resource):
    return {
        "resourceType": resource.resource_type.name,
        "description": resource.resource_description,
        "quantity": resource.resource_qty
    }


def hospital_to_json(hospital: Hospital):
    h_id = "{}-{}-{}".format(hospital.state, hospital.city, hospital.name)
    resources_json_array = [
        resource_to_json(resource) for resource in hospital.resources
    ]
    json_obj = {
        "lastUpdatedAt": hospital.last_updated.isoformat(),
        "resources": resources_json_array,
        "vendor": {
            "name": hospital.name,
            "address": {
                "completeAddress": hospital.address,
                "city": hospital.city,
                "district": hospital.district,
                "state": hospital.state
            }
        }
    }

    return json_obj


def get_host():
    return os.environ.get('INDIA_COVID_HOST')


def get_headers():
    return {
        'authorization': os.environ.get('INDIA_COVID_AUTH_HEADER'),
        'Content-Type': 'application/json'
    }


def post_request(json_obj):
    host = get_host()
    url = "http://{}/dataLeads".format(host)
    headers = get_headers()
    return requests.post(url, data=json_obj, headers=headers)


def get_request():
    host = get_host()
    url = "http://{}/dataLeads".format(host)
    return requests.get(url)