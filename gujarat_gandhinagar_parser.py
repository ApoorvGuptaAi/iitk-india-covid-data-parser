import requests

from bs4 import BeautifulSoup

from datetime import datetime
from dateutil import parser

from hospital import Hospital, Resource, ResourceType

URLS = {
    ResourceType.ICU_WITH_VENTILATOR:
    "https://vmc.gov.in/HospitalModuleGMC/HospitalBedsDetails.aspx?tid=2",
    ResourceType.ICU_WITHOUT_VENTILATOR:
    "https://vmc.gov.in/HospitalModuleGMC/HospitalBedsDetails.aspx?tid=3",
    ResourceType.BED_WITH_OXYGEN:
    "https://vmc.gov.in/HospitalModuleGMC/HospitalBedsDetails.aspx?tid=4",
    ResourceType.BED_WITHOUT_OXYGEN:
    "https://vmc.gov.in/HospitalModuleGMC/HospitalBedsDetails.aspx?tid=5"
}


def createBaseHospital(tableRowEl, hospitals):
    tds = tableRowEl.find_all("td")
    nameEl = tds[0]
    name = nameEl.get_text()
    if name not in hospitals:
        hospital = Hospital(name)
        hospital.last_updated = parser.parse(tds[7].get_text() + "+05:30",
                                             dayfirst=True)
        hospital.url = nameEl.find('a')['href']
        hospital.address = tds[1].get_text()
        hospital.state = "Gujarat"
        hospital.district = "Gandhinagar"
        hospitals[name] = hospital
        hospital.resources = []
    return hospitals[name]


def parseResource(tableRowEl, hospital, r_type):
    tds = tableRowEl.find_all("td")
    total = int(tds[2].get_text())
    available = int(tds[4].get_text())
    r = Resource(r_type, '', available, total)
    hospital.resources.append(r)


def get_data():
    hospitals = {}
    for r_type in URLS:
        url = URLS[r_type]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tableEl = soup.find("table")
        for hospitalEl in tableEl.find_all("tr")[1:]:
            hospital = createBaseHospital(hospitalEl, hospitals)
            parseResource(hospitalEl, hospital, r_type)
    return {
        "https://vmc.gov.in/HospitalModuleGMC/Default.aspx": hospitals.values()
    }
