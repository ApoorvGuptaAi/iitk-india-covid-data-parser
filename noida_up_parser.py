import requests
import dateutil.parser

from hospital import Hospital, Resource, ResourceType
from database_helper import upload_hospitals

# List of web data sources
NOIDA_URL = 'https://safe-waters-75143.herokuapp.com/hospitals'


def get_data_from_web():
    return requests.get(NOIDA_URL).json()


def get_hospital_data(hosp_data):
    resources = [
        Resource(ResourceType.ICU_WITH_VENTILATOR, 'Vacant_ventilator',
                 int(hosp_data['Vacant_ventilator'])),
        Resource(ResourceType.BED_WITH_OXYGEN, 'Vacant_oxygen',
                 int(hosp_data['Vacant_oxygen'])),
        Resource(ResourceType.BED_WITHOUT_OXYGEN, 'Vacant_normal',
                 int(hosp_data['Vacant_normal']))
    ]
    hosp = Hospital(hosp_data['name'], hosp_data['address'],
                    'Gautam Buddh Nagar', 'Noida', 'Uttar Pradesh',
                    hosp_data['location_url'],
                    dateutil.parser.isoparse(hosp_data['updated_at']),
                    resources)
    hosp.url = NOIDA_URL
    hosp.debug_data = str(hosp_data)
    return hosp


def get_noida_hospitals():
    scraped_data = get_data_from_web()
    return {
        NOIDA_URL: [get_hospital_data(hospital) for hospital in scraped_data]
    }


def main():
    hospital_data = get_noida_hospitals()
    #upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()