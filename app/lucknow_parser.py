import logging
import threading
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from dateutil import parser
from hospital import Hospital, Resource, ResourceType
from generic_html_parser import HtmlHospitalParser

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class MyOpener(urllib.request.FancyURLopener):
    # version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17'
    version = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0'


class UttarParser(HtmlHospitalParser):
    URL = "https://beds.dgmhup-covid19.in/EN/covid19bedtrack/"
    hospital_state = 'Uttar Pradesh'

    def __init__(self):
        self.hospitals = []
        self.opener = MyOpener()

    def parse_hospitals(self, district_filter=None):
        with self.opener.open(self.URL) as f:
            soup = BeautifulSoup(f, 'html.parser')
            viewstate = soup.select("#__VIEWSTATE")[0]['value']
            viewstate_gen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
            event_val = soup.select("#__EVENTVALIDATION")[0]['value']
            all_districts = soup.find('select', {'id': "MainContent_EN_ddDistrict"}).find_all('option')
            all_districts = [x.get_text().strip() for x in all_districts
                             if 'select' not in x.get_text().strip().lower()]
            if district_filter:
                if type(district_filter) != list:
                    district_filter = [district_filter]
                district_filter = [x.upper() for x in district_filter]
            else:
                district_filter = all_districts
        for district in district_filter:
            if district not in all_districts:
                raise Exception(f'Passed in district: {district} that does not map to existing '
                                f'ones: {all_districts}')
            form_data = self._gen_request(viewstate, viewstate_gen, event_val, district)
            encoded_fields = urllib.parse.urlencode(form_data)
            with self.opener.open(self.URL, encoded_fields) as f:
                soup = BeautifulSoup(f, 'html.parser')
                hospital_keys = [x.get_text().strip() for x in soup.find_all('span')][3:]
                hospital_keys = [tuple(hospital_keys[i:i + 5]) for i in range(0, len(hospital_keys), 5)]
                hospital_keys = [x for x in hospital_keys if x[0] and len(x) == 5]
                update_links = [x['href'].split("\'")[1] for x in soup.find_all('a', {'class': 'style98'})][::2]
                viewstate = soup.select("#__VIEWSTATE")[0]['value']
                viewstate_gen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
                event_val = soup.select("#__EVENTVALIDATION")[0]['value']
                assert len(hospital_keys) == len(update_links), "Could not match up the hospital keys " \
                                                                "with the update links"
            self.add_hospitals(hospital_keys, update_links, viewstate, viewstate_gen, event_val, district)
            if not self.hospitals:
                raise Exception(f'Could not pick up any hospitals - schema likely changed for {self.URL}')
            logger.info(f'Picked up a total of {len(self.hospitals)} hospitals in '
                        f'{district}')
        return self

    def add_hospitals(self, hospital_keys, update_links, viewstate, viewstate_gen, event_val, district):
        encoded_datas = [urllib.parse.urlencode(
            self._gen_request(viewstate, viewstate_gen, event_val, district, detail=update_data))
            for update_data in update_links]
        ou = gather_results([run_item(self.read_hospital, hosp_data, encoded_data, district)
                             for hosp_data, encoded_data in
                             zip(hospital_keys, encoded_datas)])
        logger.info(f'Added {len(ou)} hospitals')

    def read_hospital(self, hosp_data, encoded_fields, district):
        with self.opener.open(self.URL, encoded_fields) as f:
            soup = BeautifulSoup(f, 'html.parser')
            bed_data = [int(x.get_text()) for x in soup.find_all('span', {'class': 'style102'})]
            try:
                update_date = parser.parse(hosp_data[2] + "+05:30", dayfirst=True)
                address = hosp_data[3]
            except parser.ParserError:
                update_date = parser.parse(hosp_data[3] + "+05:30", dayfirst=True)
                address = hosp_data[2]
            hospital = Hospital(**{'name': hosp_data[0],
                                   'resources': self._resources_from_bed_data(bed_data),
                                   'address': address.strip(),
                                   'district': district,
                                   'url': self.URL,
                                   'state': self.hospital_state,
                                   'last_updated': update_date})
            self.hospitals.append(hospital)

    @staticmethod
    def _resources_from_bed_data(bed_data):
        ret_resources = []
        resource_types = [ResourceType.BED_WITHOUT_OXYGEN, ResourceType.BED_WITH_OXYGEN, ResourceType.ICUS]
        idx = 0
        for resource_type in resource_types:
            if bed_data[idx] == 0:
                idx += 1
                continue
            ret_resources.append(Resource(resource_type, '', bed_data[idx + 3], bed_data[idx]))
            idx += 1
        return ret_resources

    @staticmethod
    def _gen_request(viewstate, viewstate_gen, event_val, district, detail=None):
        if detail:
            return (
                ('ctl00$ScriptManager1', f"ctl00$MainContent_EN$UpdatePanel3|{detail}"),
                ('__EVENTTARGET', f"{detail}"),
                ('__EVENTARGUMENT', ''),
                ('__LASTFOCUS', ''),
                ('__VIEWSTATE', viewstate),
                ('__VIEWSTATEGENERATOR', viewstate_gen),
                ('__EVENTVALIDATION', event_val),
                ("ctl00$MainContent_EN$ddDistrict", district),
                ('ctl00$MainContent_EN$ddFacility', 'All'),
                ('ctl00$MainContent_EN$ddFacilityType', 'All Type'),
                ('ctl00$MainContent_EN$ddBedAva', 'All')
            )
        return (
            ('__EVENTTARGET', "ctl00$MainContent_EN$ddDistrict"),
            ('__EVENTARGUMENT', ''),
            ('__LASTFOCUS', ''),
            ('__VIEWSTATE', viewstate),
            ('__VIEWSTATEGENERATOR', viewstate_gen),
            ('__EVENTVALIDATION', event_val),
            ("ctl00$MainContent_EN$ddDistrict", district),
            ('ctl00$MainContent_EN$ddFacility', 'All'),
            ('ctl00$MainContent_EN$ddFacilityType', 'All Type'),
            ('ctl00$MainContent_EN$ddBedAva', 'All'),
            ('ctl00$MainContent_EN$Button2', 'Submit')
        )

    @staticmethod
    def export_hospital_data(district_filter=None):
        lucknow_parser = UttarParser().parse_hospitals(district_filter)
        return {lucknow_parser.URL: lucknow_parser.hospitals}


def run_item(f, item, item2, item3):
    result_info = [threading.Event(), None]

    def runit():
        result_info[1] = f(item, item2, item3)
        result_info[0].set()

    threading.Thread(target=runit).start()
    return result_info


def gather_results(result_infos):
    results = []
    for i in range(len(result_infos)):
        result_infos[i][0].wait()
        results.append(result_infos[i][1])
    return results


def get_hospital_data(district_filter=None):
    return UttarParser.export_hospital_data(district_filter)
