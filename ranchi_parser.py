from bs4 import BeautifulSoup
import requests
from hospital import Hospital, Resource, ResourceType
from datetime import datetime
from database_helper import upload_hospitals

RANCHI_URL = 'https://pratirakshak.co.in/new-report.php'
HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
}
COL_NAMES = [
    'hosp_name', 'hosp_contact', 'ic_contact', 'No_Oxygen_Total',
    'No_Oxygen_Occupied', 'No_Oxygen_Available', 'Oxygen_Total',
    'Oxygen_Occupied', 'Oxygen_Available', 'ICU_Total', 'ICU_Occupied',
    'ICU_Available', 'last_updated'
]


def get_ranchi_hospitals():
    hospital_data = []
    page = requests.get(RANCHI_URL, headers=HEADERS)
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find('table')
    for row in tables.find_all('tr'):
        row_data = [d.text for d in row.find_all('td')]
        if not row_data:
            continue
        row_data = {c: r for r, c in zip(row_data, COL_NAMES)}
        last_updated = datetime.strptime(row_data['last_updated'],
                                         '%Y-%m-%d %H:%M:%S')
        resources = [
            Resource(ResourceType.BED_WITHOUT_OXYGEN, None,
                     row_data['No_Oxygen_Available']),
            Resource(ResourceType.BED_WITH_OXYGEN, None,
                     row_data['Oxygen_Available']),
            Resource(ResourceType.ICUS, None, row_data['ICU_Available'])
        ]
        hosp = Hospital(row_data['hosp_name'], None, 'Ranchi', 'Ranchi',
                        'Jharkhand', '', last_updated, resources)
        hospital_data.append(hosp)
    return hospital_data


def main():
    hospital_data = get_ranchi_hospitals()
    #print(hospital_data)
    #upload_hospitals(hospital_data)


if __name__ == "__main__":
    main()