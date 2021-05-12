import requests
import logging
from bs4 import BeautifulSoup
from dateutil import parser
from hospital import Hospital, Resource, ResourceType
from generic_html_parser import HtmlHospitalParser


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class PanvelParser(HtmlHospitalParser):
    URL = "https://covidbedpanvel.in/HospitalInfo/showindex"
    hospital_district = 'Navi Mumbai'
    hospital_city = 'Panvel'
    hospital_state = 'Maharashtra'

    def __init__(self):
        self.page_soup = None
        self.hospitals = []

    def read_page(self):
        response = requests.get(self.URL)
        self.page_soup = BeautifulSoup(response.text, 'html.parser')
        return self

    def parse_hospitals(self):
        hospital_containers = self.page_soup.find_all("div", {"class": "row"})
        container_idx = 0
        for hosp_cont in hospital_containers:
            try:
                self.load_hospital_from_row(hosp_cont)
            except Exception as e:
                logger.warning(f'Cannot parse line {container_idx}: {e}')
            container_idx += 1
        if not self.hospitals:
            raise Exception(f'Could not pick up any hospitals - schema likely changed for {self.URL}')
        logger.info(f'Picked up a total of {len(self.hospitals)} hospitals in {self.hospital_district} - '
                    f'{self.hospital_city}')
        return self

    def load_hospital_from_row(self, container):
        name_elem = container.find('h4')
        if not name_elem:
            raise Exception(f'Cannot read name of hospital')
        resource_mapper = {'ICU Vacant': ResourceType.ICUS,
                           'Non ICU Vacant': ResourceType.BEDS,
                           'Ventilator Available': ResourceType.ICU_WITH_VENTILATOR}
        categories = [x.get_text() for x in container.find_all("div", {'class': 'text-white mb-0'})]
        numbers = [int(x.find_all('b')[0].get_text()) for x in container.find_all("div", {'class': 'h1 m-0'})]
        hospital_name = name_elem.get_text()
        assert categories == ['Capacity', 'Occupied', 'Vacant',
                              'ICU Vacant', 'Non ICU Vacant', 'Ventilator Available'], f"Cant read categories"
        assert len(categories) == len(numbers), f"Unable to match up numbers and categories for {hospital_name} details"
        resource_dict = {k: v for k, v in zip(categories, numbers)}
        resources = []
        for resource_name, resource_type in resource_mapper.items():
            resources.append(Resource(resource_type, '', resource_dict[resource_name]))
        time_stamp = container.find('span', {'class': 'pull-right'}).get_text().split('Updated :')[-1]
        hospital = Hospital(**{'name': hospital_name,
                               'resources': resources,
                               'district': self.hospital_district,
                               'city': self.hospital_city,
                               'url': self.URL,
                               'state': self.hospital_state,
                               'last_updated': parser.parse(time_stamp, dayfirst=True),
                               'debug_text': str(container)})
        self.hospitals.append(hospital)
        logger.info(f'Parsed hospital: {hospital.name} with {len(hospital.resources)} resources')

    @staticmethod
    def export_hospital_data():
        panvel_parser = PanvelParser().read_page().parse_hospitals()
        return {panvel_parser.URL: panvel_parser.hospitals}


def get_hospital_data():
    return PanvelParser.export_hospital_data()


# Uncomment for test
# if __name__ == '__main__':
#     dat = get_hospital_data()
#     logger.info(f'Test complete')
