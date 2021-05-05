from typing import Optional
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser

from hospital import Hospital, Resource, ResourceType

URL = "https://nmmchealthfacilities.com/HospitalInfo/showhospitalist"


def get_headers(tableElem):
    ths = tableElem.find("tr").find_all("th")
    return [th.get_text() for th in ths]


def get_row_names(tableElem):
    trs = tableElem.find_all("tr")[1:]
    return [tr.find('td').get_text() for tr in trs]


def get_cell(tableElem, row, column):
    return int(
        tableElem.find_all('tr')[row + 1].find_all('td')[column + 1].get_text())


def parseHospital(hospitalDiv) -> Optional[Hospital]:
    nameElem = hospitalDiv.find("h4")
    tableElem = hospitalDiv.find("table")
    if not nameElem or not tableElem:
        return None
    if (get_headers(tableElem)) != [
            '', 'Capacity', 'Occupancy', 'Available'
    ] or get_row_names(tableElem) != [
            'ICU', 'With O2', 'Without O2', 'Ventilator'
    ]:
        raise AssertionError("HTML schema changed")
    resource_types = [
        ResourceType.ICUS, ResourceType.BED_WITH_OXYGEN,
        ResourceType.BED_WITHOUT_OXYGEN, ResourceType.ICU_WITH_VENTILATOR
    ]
    resources = []
    for (index, r_type) in enumerate(resource_types):
        r = Resource(r_type, '', get_cell(tableElem, index, 2),
                     get_cell(tableElem, index, 0))
        resources.append(r)
    hospital = Hospital(nameElem.get_text())
    hospital.resources = resources
    print(hospital)
    hospital.district = "Navi Mumbai"
    hospital.state = "Maharashtra"
    hospital.last_updated = datetime.utcfromtimestamp(0)
    hospital.debug_text = str(hospitalDiv)
    return hospital


def get_hospital_data():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    containerDiv = soup.find("div", {"class": "container"})
    hospitalContainerDivs = soup.find_all("div", {"class": "row"})[3]
    hospitalDivs = hospitalContainerDivs.find_all("div", {"class": "row"})
    hospitals = []
    for hospitalDiv in hospitalDivs:
        hospital = parseHospital(hospitalDiv)
        if hospital:
            hospitals.append(hospital)
    return {URL: hospitals}
