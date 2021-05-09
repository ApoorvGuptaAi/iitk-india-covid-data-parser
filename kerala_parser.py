import requests
import datetime

from bs4 import BeautifulSoup

from hospital import Hospital, Resource, ResourceType

URL_BASE = 'https://covid19jagratha.kerala.nic.in/home/addHospitalDashBoard'

OXYGEN_BED_URL = "https://covid19jagratha.kerala.nic.in/home/getOxygenBedCount"
OXYGEN_TOTAL_INDEX = 1
OXYGEN_AVAIL_INDEX = 2

HOSPITAL_DATA_URL = "https://covid19jagratha.kerala.nic.in/home/getDistHospitalCount"
NAME_INDEX = 0
BED_INDEX = 1
ICU_TOTAL_INDEX = 2
ICU_W_VENTILATOR_INDEX = 3
BED_AVAIL_INDEX = 4
ICU_AVAILABILITY_INDEX = 5
ICU_W_VENTILATOR_AVAIL_INDEX = 6


def get_district_page_url(index):
    return URL_BASE + "?distId={}&infraType=TRUE".format(index)


def get_base_page_url():
    return URL_BASE


def get_district_data(index):
    url = get_district_page_url(index)
    print(url)
    # Use session to share cookies.
    with requests.session() as session:
        session.get(url, verify=False)
        oxygen_bed_resp = session.get(OXYGEN_BED_URL, verify=False).json()
        hospital_data_resp = session.get(HOSPITAL_DATA_URL, verify=False).json()
    return hospital_data_resp, oxygen_bed_resp, url


def create_hospitals(district_name, data):
    hospitals = []
    oxygen_bed_data = {entry[0]: entry for entry in data[1]}
    for entry in data[0]:
        name = entry[0]
        hospital = Hospital(name)
        hospital.state = "Kerala"
        hospital.district = district_name
        hospital.url = data[2]
        hospital.resources = []
        epoch_secs_str = entry[9]
        epoch_secs = float(epoch_secs_str) / 1000 if epoch_secs_str else 0
        tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        dt = datetime.datetime.fromtimestamp(epoch_secs, tz)
        hospital.last_updated = dt
        hospital.resources.append(
            Resource(ResourceType.BEDS, '', int(entry[BED_AVAIL_INDEX]),
                     int(entry[BED_INDEX])))
        hospital.resources.append(
            Resource(ResourceType.ICU_WITH_VENTILATOR, '',
                     int(entry[ICU_W_VENTILATOR_AVAIL_INDEX]),
                     int(entry[ICU_W_VENTILATOR_INDEX])))
        hospital.resources.append(
            Resource(ResourceType.ICUS, '', int(entry[ICU_AVAILABILITY_INDEX]),
                     int(entry[ICU_TOTAL_INDEX])))
        oxygen_entry = oxygen_bed_data.get(name, None)
        if oxygen_entry:
            hospital.resources.append(
                Resource(ResourceType.BED_WITH_OXYGEN, '',
                         int(oxygen_entry[OXYGEN_AVAIL_INDEX]),
                         int(oxygen_entry[OXYGEN_TOTAL_INDEX])))
        hospitals.append(hospital)

    return hospitals


def get_data():
    base_page = requests.get(get_base_page_url(), verify=False)
    soup = BeautifulSoup(base_page.text, 'html.parser')
    selectEl = soup.find("select", {"id": "distId"})
    options = selectEl.contents[1:]
    districts_data = {
        int(option["value"]): option.get_text()
        for option in options
        if not isinstance(option, str)
    }
    del districts_data[0]
    print(districts_data)
    return_data = {}
    for distId in districts_data:
        data = get_district_data(distId)
        hospitals = create_hospitals(districts_data[distId], data)
        return_data[data[2]] = hospitals
    return return_data
