from bs4 import BeautifulSoup
import requests
from hospital import Hospital, Resource, ResourceType
from datetime import datetime
from database_helper import upload_hospitals

HOSPITAL_URL = 'https://covidinfo.rajasthan.gov.in/Covid-19hospital-wisebedposition-wholeRajasthan.aspx'

COL_NAMES = [
    'hosp_index', 
    'district', 
    'hosp_name', 
    'general_beds_total',
    'general_beds_occupied',
    'general_beds_available',
    'oxygen_beds_total',
    'oxygen_beds_occupied',
    'oxygen_beds_available',
    'icu_without_ventilator_beds_total',
    'icu_without_ventilator_beds_occupied',
    'icu_without_ventilator_beds_available',
    'icu_with_ventilator_beds_total',
    'icu_with_ventilator_beds_occupied',
    'icu_with_ventilator_beds_available',
    'hospital_helpline',
    'district_control_line'
]

def get_rajasthan_hospitals():
    hospital_data = []
    req_obj = requests.Session()
    page = req_obj.get(HOSPITAL_URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find('table')
    # Skip the first row as it is about totals
    for row in tables.find('tbody').find_all('tr')[1:]:
        row_data = [d.text for d in row.find_all('td')]
        if not row_data:
            continue
    
        row_data = {c: r for r, c in zip(row_data, COL_NAMES)}
        resources = [
            Resource(
                resource_type = ResourceType.BED_WITHOUT_OXYGEN,
                resource_description = None,
                resource_qty = int(row_data['general_beds_available']),
                total_qty = int(row_data['general_beds_total'])
            ), Resource(
                resource_type = ResourceType.BED_WITH_OXYGEN,
                resource_description = None,
                resource_qty = int(row_data['oxygen_beds_available']),
                total_qty = int(row_data['oxygen_beds_total'])
            ), Resource(
                resource_type = ResourceType.ICU_WITH_VENTILATOR,
                resource_description = None,
                resource_qty = int(row_data['icu_with_ventilator_beds_available']),
                total_qty = int(row_data['icu_with_ventilator_beds_total'])
            ), Resource(
                resource_type = ResourceType.ICU_WITHOUT_VENTILATOR,
                resource_description = None,
                resource_qty = int(row_data['icu_without_ventilator_beds_available']),
                total_qty = int(row_data['icu_without_ventilator_beds_total'])
            )
        ]
        hosp = Hospital(row_data['hosp_name'], None, row_data['district'], None,
                        'Rajasthan', '', datetime.fromtimestamp(0), resources)
        hosp.url = HOSPITAL_URL
        hosp.debug_text = str(row_data)
        hospital_data.append(hosp)
    return {HOSPITAL_URL: hospital_data}


def main():
    hospital_data = get_rajasthan_hospitals()
    print(len(hospital_data[HOSPITAL_URL]))
    print(hospital_data)
    #upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()
