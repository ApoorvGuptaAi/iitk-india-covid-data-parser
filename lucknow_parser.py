import requests
import logging
from bs4 import BeautifulSoup
from dateutil import parser
from hospital import Hospital, Resource, ResourceType
from generic_html_parser import HtmlHospitalParser


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class LucknowParser(HtmlHospitalParser):
    URL = "https://beds.dgmhup-covid19.in/EN/covid19bedtrack"
    hospital_city = 'Lucknow'
    hospital_state = 'Uttar Pradesh'

    def __init__(self):
        self.page_soup = None
        self.hospitals = []

    def read_page(self):
        response = requests.get(self.URL)
        self.page_soup = BeautifulSoup(response.text, 'html.parser')
        return self

    def parse_hospitals(self):
        hospital_keys = [x.get_text().strip() for x in self.page_soup.find_all('span')][3:]
        hospital_values = [x.get_text() for x in self.page_soup.find_all('a', {'class': 'style98'})]
        hospital_values = [tuple(hospital_values[i:i + 2]) for i in range(0, len(hospital_values), 2)]
        hospital_keys = [tuple(hospital_keys[i:i + 5]) for i in range(0, len(hospital_keys), 5)]
        hospital_keys = [x for x in hospital_keys if x[0] and len(x) == 5]
        assert len(hospital_keys) == len(hospital_values), "Could not match up the hospital keys with hospital values " \
                                                           "- may be a change in schema"
        num_hospitals = len(hospital_keys)
        logger.info(f'Picked up data for {num_hospitals} hospitals in {self.hospital_city}')
        hospital_idx = 0
        for key_tupl, val_tupl in zip(hospital_keys, hospital_values):
            try:
                resources = [Resource(ResourceType.BEDS, '', int(val_tupl[1]), int(val_tupl[0]))]
                # TODO: This is a dynamic site that will provide more details on ICU/OXYGEN on click...figure that out
                try:
                    update_date = parser.parse(key_tupl[2] + "+05:30", dayfirst=True)
                    address = key_tupl[3]
                except parser.ParserError:
                    update_date = parser.parse(key_tupl[3] + "+05:30", dayfirst=True)
                    address = key_tupl[2]
                hospital = Hospital(**{'name': key_tupl[0],
                                       'resources': resources,
                                       'address': address.strip(),
                                       'city': self.hospital_city,
                                       'url': self.URL,
                                       'state': self.hospital_state,
                                       'last_updated': update_date})
                self.hospitals.append(hospital)
                logger.info(f'Parsed hospital: {hospital.name} with {len(hospital.resources)} resources')
            except Exception as e:
                logger.warning(f'Cannot parse hospital idx {hospital_idx}: {e}')
        if not self.hospitals:
            raise Exception(f'Could not pick up any hospitals - schema likely changed for {self.URL}')
        logger.info(f'Picked up a total of {len(self.hospitals)} hospitals in '
                    f'{self.hospital_city}')
        return self

    @staticmethod
    def export_hospital_data():
        lucknow_parser = LucknowParser().read_page().parse_hospitals()
        return {lucknow_parser.URL: lucknow_parser.hospitals}


def get_hospital_data():
    return LucknowParser.export_hospital_data()
