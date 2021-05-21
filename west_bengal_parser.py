"""
NOTE: Scraping aspx is more complex than a list of URLs - these websites store data in requests and responses
- The _VIEWSTATE field is passed around with each POST request that the browser makes to the server
- The server then decodes and loads the client's UI state, computes values for the new view state and
    renders the resulting page with the new view state as a hidden field

- open up the developer view on the URL & the Network tab
    - you should see a request made to some main file ".aspx"
        - check the response and it leads you to the request details



"""

import logging
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from dateutil import parser
from hospital import Hospital, Resource, ResourceType
from generic_html_parser import HtmlHospitalParser

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class MyOpener(urllib.request.FancyURLopener):
    version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17'


class WestBengalParser(HtmlHospitalParser):
    URL = "https://excise.wb.gov.in/CHMS/Public//Page/CHMS_Public_Hospital_Bed_Availability.aspx"
    hospital_state = 'West Bengal'

    def __init__(self):
        self.page_soup = None
        self.hospitals = []

    def parse_hospitals(self, district_filter=None):
        myopener = MyOpener()
        with myopener.open(self.URL) as f:
            soup = BeautifulSoup(f, 'html.parser')
            viewstate = soup.select("#__VIEWSTATE")[0]['value']
            viewstate_gen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
            all_districts = soup.find('select', {'id': "ctl00_ContentPlaceHolder1_ddl_District"}).find_all('option')
            if district_filter:
                if not type(district_filter) == list:
                    district_filter = [district_filter]
                district_filter = [x.upper() for x in district_filter]
                for filtered_district in district_filter:
                    assert filtered_district in [x.get_text().strip() for x in all_districts], \
                        f"{filtered_district} " \
                        f"passed in does not map to any existing district in West Bengal: " \
                        f"{[x.get_text().strip() for x in all_districts]}"
            for district in all_districts:
                if district.get_text() == '--Select--':
                    continue
                if district_filter:
                    if district.get_text().strip() not in district_filter:
                        continue
                for gov_flag in ['G', 'R', 'P']:
                    form_data = self._gen_request(viewstate, viewstate_gen, district, gov_flag)
                    encoded_fields = urllib.parse.urlencode(form_data)
                    with myopener.open(self.URL, encoded_fields) as f1:
                        hot_soup = BeautifulSoup(f1.read(), 'html.parser')
                        pagination = hot_soup.find('tr', {'class': 'pagination-ys'})
                        if not pagination:
                            pages = [1]
                        else:
                            pages = [x for x in range(1, int(pagination.find_all('a')[-1].get_text()) + 1)]
                        for page in pages:
                            form_data = self._gen_request(viewstate, viewstate_gen, district, gov_flag, page)
                            encoded_fields = urllib.parse.urlencode(form_data)
                            with myopener.open(self.URL, encoded_fields) as f2:
                                hot_soup = BeautifulSoup(f2.read(), 'html.parser')
                                schema_validation = hot_soup.find_all('div',
                                                                      {'class': 'card-header bg-light text-center'})
                                if len(schema_validation) == 0:
                                    logger.info(f'Did not pick up any hospitals for {district} - {gov_flag}')
                                    continue
                                assert [x.get_text().strip() for x in schema_validation[:5]] == \
                                       ['Covid Beds (Regular)', 'Covid Beds with Oxygen Support',
                                        'HDU Beds (Covid)',
                                        'CCU Beds (Covid - without ventilator)',
                                        'CCU Beds (Covid - with ventilator)'], \
                                    f'The schema seems to have changed at {self.URL}'
                                all_hospital_names = [x.get_text().strip() for x in
                                                      hot_soup.find('div', {'class': "form-group row"}).find_all('h5')]
                                districts_and_cities = [x.get_text().replace('\n', '').replace('\r', '') for x in
                                                        hot_soup.find('div', {'class': "form-group row"}).
                                                            find_all('div',
                                                                     {
                                                                         'class': 'card-text col-md-12 col-lg-12 col-sm-12 col-xs-12'})]
                                districts_and_cities = [[y.strip() for y in x.split(',')] for x in districts_and_cities]
                                dates_updated = [parser.parse(x.get_text().split('Updated On :')[-1].strip() + '+05:30')
                                                 for x in
                                                 hot_soup.find_all('div', {'class': "card-footer text-muted"})]
                                total_beds = hot_soup.find_all('h3', {'class': 'text-primary'})
                                vacant_beds = hot_soup.find_all('h3', {'class': 'text-success'})
                                assert len(vacant_beds) == len(total_beds)
                                assert len(vacant_beds) / len(all_hospital_names) == 24
                                total_beds = [list(total_beds[i:i + 24]) for i in range(0, len(total_beds), 24)]
                                vacant_beds = [list(vacant_beds[i:i + 24]) for i in range(0, len(vacant_beds), 24)]
                                for i in range(len(all_hospital_names)):
                                    self.hospitals.append(
                                        Hospital(**{
                                            'name': all_hospital_names[i],
                                            'address': ','.join(districts_and_cities[i][:-1]),
                                            'city': districts_and_cities[i][-1],
                                            'district': district.get_text().strip(),
                                            'url': self.URL,
                                            'state': self.hospital_state,
                                            'last_updated': dates_updated[i],
                                            'resources': self._read_resource_data(total_beds[i], vacant_beds[i])
                                        }))
                                logger.info(f'Done parsing {len(all_hospital_names)} hospitals in {district}')
            return self

    @staticmethod
    def _gen_request(viewstate, viewstate_gen, district, govt_flag, page=1):
        if page == 1:
            return (
                ("ctl00$ScriptManager1",
                 "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$ddl_District"),
                ('__EVENTTARGET', "ctl00$ContentPlaceHolder1$ddl_District"),
                ('__VIEWSTATE', viewstate),
                ('__VIEWSTATEGENERATOR', viewstate_gen),
                ('__VIEWSTATEENCRYPTED', ''),
                ('__LASTFOCUS', ''),
                ('__EVENTARGUMENT', ''),
                ('__VIEWSTATEENCRYPTED', ''),
                ('ctl00$ContentPlaceHolder1$ddl_District', district['value']),
                ('ctl00$ContentPlaceHolder1$rdo_Govt_Flag', govt_flag))

        return (
            ("ctl00$ScriptManager1",
             "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$ddl_District"),
            ('__EVENTTARGET', "ctl00$ContentPlaceHolder1$GridView2"),
            ('__VIEWSTATE', viewstate),
            ('__VIEWSTATEGENERATOR', viewstate_gen),
            ('__VIEWSTATEENCRYPTED', ''),
            ('__LASTFOCUS', ''),
            ('__EVENTARGUMENT', f'Page${page}'),
            ('__VIEWSTATEENCRYPTED', ''),
            ('ctl00$ContentPlaceHolder1$ddl_District', district['value']),
            ('ctl00$ContentPlaceHolder1$rdo_Govt_Flag', govt_flag)
        )

    @staticmethod
    def _read_resource_data(total_beds: list, avail_beds: list):
        total_beds = [int(x.get_text()) for x in total_beds]
        avail_beds = [int(x.get_text()) for x in avail_beds]
        resource_mapper = [(ResourceType.BED_WITHOUT_OXYGEN, 7),
                           (ResourceType.BED_WITH_OXYGEN, 11),
                           (ResourceType.BEDS, 15),
                           (ResourceType.ICU_WITHOUT_VENTILATOR, 19),
                           (ResourceType.ICU_WITH_VENTILATOR, 23)]
        resources_to_return = []
        for idx in range(len(resource_mapper)):
            if total_beds[resource_mapper[idx][1]] == 0:
                continue
            resources_to_return.append(
                Resource(resource_mapper[idx][0], '', avail_beds[resource_mapper[idx][1]],
                         total_beds[resource_mapper[idx][1]]))
        return resources_to_return

    @staticmethod
    def export_hospital_data(districts=None):
        west_bengal_parser = WestBengalParser().parse_hospitals(districts)
        logger.info(f'Picked up {len(west_bengal_parser.hospitals)} hospitals in West Bengal')
        return {west_bengal_parser.URL: west_bengal_parser.hospitals}


def get_hospital_data(districts=None):
    return WestBengalParser.export_hospital_data(districts)
