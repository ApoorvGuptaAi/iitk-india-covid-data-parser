from bs4 import BeautifulSoup
import requests
from hospital import Hospital, Resource, ResourceType
from datetime import datetime

PRAYAGRAJ_URL = 'http://monitor.covid19reportprayagraj.in/hospitalbeds.aspx'
COL_NAMES = ['Hospital Name', 'Last Updated', 'Bed Type', 'Capacity', 'Vacant']

def get_prayagraj_hospitals():
    hospital_data = []
    page = requests.get(PRAYAGRAJ_URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find('table', {})
    for row in table.find_all('tr'):
        row_data = [col.text.strip() for col in row.find_all('td')]
        if not row_data or len(row_data) != len(COL_NAMES) or row_data == COL_NAMES:
            continue
        row_data = {c: r for r, c in zip(row_data, COL_NAMES)}

        # reformat information
        last_updated = datetime.strptime(row_data['Last Updated'].replace('\n', ' '),
                                         '%d-%m-%Y %I:%M%p')
        bed_types = row_data['Bed Type'].split(' \n')
        bed_capacity = row_data['Capacity'].split('\n\n')
        bed_avail= row_data['Vacant'].split('\n')
        for i in range(len(bed_types)):
            row_data[bed_types[i] + '_vacant'] = int(bed_avail[i])
            row_data[bed_types[i] + '_capacity'] = int(bed_capacity[i])

        resources = [
            Resource(ResourceType.ICU_WITHOUT_VENTILATOR, None, 
                     row_data['ICU_vacant'], 
                     row_data['ICU_capacity']),
            Resource(ResourceType.BED_WITHOUT_OXYGEN, None,
                     row_data['ISO !O2_vacant'] + row_data['HDU_vacant'],
                     row_data['ISO !O2_capacity']+ row_data['HDU_vacant']),
            Resource(ResourceType.BED_WITH_OXYGEN, None,
                     row_data['ISO O2_vacant'],
                     row_data['ISO O2_capacity']),
            Resource(ResourceType.ICU_WITH_VENTILATOR, None, 
                     row_data['Ventilator_vacant'],
                     row_data['Ventilator_capacity']),
        ]
        hospital_info = row_data['Hospital Name'].split('\n')
        hospital_name, address = hospital_info[:2] if len(hospital_info) > 2 else hospital_info[:2], ""
        hosp = Hospital(hospital_name, address.strip(), 'Prayagraj', 'Prayagraj',
                        'Uttar Pradesh', '', last_updated, resources)
        hosp.url = PRAYAGRAJ_URL
        hosp.debug_text = str(row_data)
        hospital_data.append(hosp)
    return {PRAYAGRAJ_URL: hospital_data}