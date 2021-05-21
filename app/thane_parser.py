from bs4 import BeautifulSoup
import requests
from hospital import Hospital, Resource, ResourceType
from datetime import datetime
from database_helper import upload_hospitals

HOSPITAL_URL = 'https://covidbedthane.in/HospitalInfo/showindex'

COL_NAMES = {
    'hosp_name': 'hosp_name', 
    'hospital_helpline': 'hospital_helpline',
    'Capacity': 'total_capacity',
    'Occupied': 'total_occupied',
    'Vacant': 'total_vacant',
    'ICU Vacant': 'icu_vacant',
    'Non ICU Vacant': 'non_icu_vacant'
}

def get_hospital_name(hospital_div):
    try:
        return hospital_div.select('.p-2 .text-center')[0].find_all('h4')[0].text
    except Exception:
        return None  

def get_hospital_bed_data(hospital_div):
    bed_data = {}

    try:
        bed_data['hospital_helpline'] = hospital_div.select('.p-2 .text-center')[0].find_all('a')[0].text
    except Exception:
        bed_data['hospital_helpline'] = "N/A"

    data_divs = hospital_div.select('.card-body.mt-12 .card-body')
    for data_div in data_divs:
        divs = data_div.select('div')
        if (len(divs) != 2):
            continue
            
        key = divs[1].text.strip()
        value = divs[0].text.strip()
        try:
            bed_data[COL_NAMES[key]] = 0 if len(value) == 0 else int(value)
        except Exception:
            print('====> [Error] Skipping bad data ' + key + ':' + value)
    
    return bed_data

def get_thane_hospitals():
    hospitals_data = []
    page = requests.get(HOSPITAL_URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    hospitals_divs = soup.select('.row .col-12')

    invalid_hosp = 0
    for div in hospitals_divs:
        name = get_hospital_name(div)
        if name is None:
            print('Skipping invalid hospital data' + str(hospital_div))
            continue
        
        hosp_data = {'hosp_name' : name}
        hosp_data.update(get_hospital_bed_data(div))
        resources = [
            Resource(
                resource_type = ResourceType.BEDS,
                resource_description = None,
                resource_qty = 0 if 'non_icu_vacant' not in hosp_data else hosp_data['non_icu_vacant'],
                total_qty = 0 if 'total_capacity' not in hosp_data else hosp_data['total_capacity']
            ), Resource(
                resource_type = ResourceType.ICUS,
                resource_description = None,
                resource_qty = 0 if 'icu_vacant' not in hosp_data else hosp_data['icu_vacant']
            )
        ]
        hosp = Hospital(hosp_data['hosp_name'], None, 'Thane', None,
                        'Maharashtra', '', datetime.fromtimestamp(0), resources)
        hosp.url = HOSPITAL_URL
        hosp.debug_text = str(hosp_data)
        hospitals_data.append(hosp)
    return {HOSPITAL_URL: hospitals_data}


def main():
    hospital_data = get_thane_hospitals()
    print(hospital_data)
    #upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()
