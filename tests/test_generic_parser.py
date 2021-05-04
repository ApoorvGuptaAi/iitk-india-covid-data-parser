import unittest
import json

from generic_hospital_parser import parse_hospital
from database_helper import hospital_to_json


class TestGenericParse(unittest.TestCase):

    def _commonTest(self, loaded_json_data_str, expected_serialized_hospital):
        hospital = parse_hospital(json.loads(loaded_json_data_str), "SomeState",
                                  "SomeCity")
        hospital.debug_text = None
        serialized_hospital = hospital_to_json(hospital, "SomeJobId")

        self.assertEqual(json.dumps(serialized_hospital),
                         expected_serialized_hospital)

    def testBasic(self):
        self.maxDiff = 2000
        loaded_json_data_str = """
            {"hospital_name":"Aarihant Ayurvedic & Aarihant Homoeopathic","hospital_poc_name":"Shashvat Trivedi","hospital_poc_designation":"Nodal Officer","hospital_poc_phone":"9898937787","last_updated_on":1620023390000,"charges":"PRIVATE","district":"Gandhinagar","area":"Gandhinagar","total_beds_allocated_to_covid":125,"total_icu_beds_with_ventilator":0,"total_icu_beds_without_ventilator":0,"total_beds_with_oxygen":10,"total_beds_without_oxygen":115,"available_icu_beds_with_ventilator":0,"available_icu_beds_without_ventilator":0,"available_beds_with_oxygen":0,"available_beds_without_oxygen":107,"hospital_address":"20 GROUND FLOOR SWASTIK COMPLEX BELLOW IDP SCHOOL MOTERA NR BANK OF BARODA, VILLAGE GATE, Motera Stadium Rd, opp. MOTERA, Motera, Ahmedabad, Gujarat 380005, India","pincode":"380005"}
        """
        expected_serialized_hospital = """{"lastUpdatedAt": "2021-05-02T23:29:50", "scrapedFrom": null, "jobId": "SomeJobId", "resources": [{"resourceType": "BEDS", "description": "", "quantity": 0, "total_quantity": 125}, {"resourceType": "ICU_WITH_VENTILATOR", "description": "", "quantity": 0, "total_quantity": 0}, {"resourceType": "ICU_WITHOUT_VENTILATOR", "description": "", "quantity": 0, "total_quantity": 0}, {"resourceType": "BED_WITH_OXYGEN", "description": "", "quantity": 0, "total_quantity": 10}, {"resourceType": "BED_WITHOUT_OXYGEN", "description": "", "quantity": 0, "total_quantity": 115}], "vendor": {"name": "Aarihant Ayurvedic & Aarihant Homoeopathic", "debugText": null, "uniqueId": "SomeState-Gandhinagar-SomeCity-Aarihant Ayurvedic & Aarihant Homoeopathic", "address": {"completeAddress": "20 GROUND FLOOR SWASTIK COMPLEX BELLOW IDP SCHOOL MOTERA NR BANK OF BARODA, VILLAGE GATE, Motera Stadium Rd, opp. MOTERA, Motera, Ahmedabad, Gujarat 380005, India", "city": "SomeCity", "district": "Gandhinagar", "state": "SomeState"}}}"""

        self._commonTest(loaded_json_data_str, expected_serialized_hospital)