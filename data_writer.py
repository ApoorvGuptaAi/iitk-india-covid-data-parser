from typing import List

from .hospital import Hospital

# https://0bin.net/paste/89z2HD1E#inlMdwVjYCbtd6kpYtLHfpW36pQmi7VtRq5dG9hDL2M
def resource_to_json(resource: Resource):
    return {
        "resourceType": resource.resource_type,
        "description": resource.resource_description,
        "quantity": resource.resource_qty
    }

def hospital_to_json(hospital: Hospital):
    h_id = "{}-{}-{}".format(hospital.state, hospital.city, hospital.name)
    resources_json_array = [resource_to_json(resource) for resource in hospital.resources]
    json_obj = {
        "lastUpdatedAt": "2021-05-03T06:27:27.045Z",     
        "resources": resources_json_array,
        "vendor": {
            "id": h_id,
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

def write_to_database(hospitals: List[Hospital]):
    pass
