import unittest
import json

from app.generic_hospital_parser import parse_hospital, get_bed_resources
from app.database_helper import hospital_to_json, resource_to_json


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
        expected_serialized_hospital = """{"lastUpdatedAt": "2021-05-02T23:29:50", "scrapedFrom": null, "jobId": "SomeJobId", "resources": [{"resourceType": "BEDS", "quantity": 0, "total_quantity": 125}, {"resourceType": "ICU_WITH_VENTILATOR", "quantity": 0, "total_quantity": 0}, {"resourceType": "ICU_WITHOUT_VENTILATOR", "quantity": 0, "total_quantity": 0}, {"resourceType": "BED_WITH_OXYGEN", "quantity": 0, "total_quantity": 10}, {"resourceType": "BED_WITHOUT_OXYGEN", "quantity": 107, "total_quantity": 115}], "vendor": {"name": "Aarihant Ayurvedic & Aarihant Homoeopathic", "debugText": null, "uniqueId": "SomeState-Gandhinagar-SomeCity-Aarihant Ayurvedic & Aarihant Homoeopathic", "address": {"completeAddress": "20 GROUND FLOOR SWASTIK COMPLEX BELLOW IDP SCHOOL MOTERA NR BANK OF BARODA, VILLAGE GATE, Motera Stadium Rd, opp. MOTERA, Motera, Ahmedabad, Gujarat 380005, India", "city": "SomeCity", "district": "Gandhinagar", "state": "SomeState", "pincode": "380005"}}}"""

        self._commonTest(loaded_json_data_str, expected_serialized_hospital)

    def testAdvanced(self):
        self.maxDiff = 2000
        loaded_json_data_str = """
        {"hospital_name": "Aadit Nursing Home", "hospital_poc_name": "Dr. Ankur Mehta", "hospital_poc_designation": "Nodal Officer", "hospital_poc_phone": "9537121211", "charges": "PRIVATE", "hospital_address": "2, Makarand Desai Marg, Santoor Park,Behind Mother\'s School, Shakti Nagar Society, Gotri, Vadodara, Gujarat 390021, India", "district": "Vadodara", "area": "Vadodara", "total_beds_allocated_to_covid": 10, "total_icu_beds_with_ventilator": 0, "total_icu_beds_without_ventilator": 0, "total_beds_with_oxygen": 10, "total_beds_without_oxygen": 0, "available_icu_beds_with_ventilator": 0, "available_icu_beds_without_ventilator": 0, "available_beds_with_oxygen": 0, "available_beds_without_oxygen": 0, "pincode": "390021"}"""

        expected_serialized_hospital = """{"lastUpdatedAt": "1969-12-31T16:00:00", "scrapedFrom": null, "jobId": "SomeJobId", "resources": [{"resourceType": "BEDS", "quantity": 0, "total_quantity": 10}, {"resourceType": "ICU_WITH_VENTILATOR", "quantity": 0, "total_quantity": 0}, {"resourceType": "ICU_WITHOUT_VENTILATOR", "quantity": 0, "total_quantity": 0}, {"resourceType": "BED_WITH_OXYGEN", "quantity": 0, "total_quantity": 10}, {"resourceType": "BED_WITHOUT_OXYGEN", "quantity": 0, "total_quantity": 0}], "vendor": {"name": "Aadit Nursing Home", "debugText": null, "uniqueId": "SomeState-Vadodara-SomeCity-Aadit Nursing Home", "address": {"completeAddress": "2, Makarand Desai Marg, Santoor Park,Behind Mother's School, Shakti Nagar Society, Gotri, Vadodara, Gujarat 390021, India", "city": "SomeCity", "district": "Vadodara", "state": "SomeState", "pincode": "390021"}}}"""

        self._commonTest(loaded_json_data_str, expected_serialized_hospital)

    def testResource(self):
        self.maxDiff = 2000
        loaded_json_data_str = """
        {"district":"Anuppur","hospital_name":"CHC JAITHARI","hospital_category":"Government","hospital_poc_name":"DR B P SHUKLA","hospital_poc_phone":"9893974942","total_beds_without_oxygen":0,"available_beds_without_oxygen":0,"total_beds_with_oxygen":10,"available_beds_with_oxygen":6,"total_icu_beds_without_ventilator":0,"available_icu_beds_without_ventilator":0,"last_updated_on":1620099796000,"area":"Anuppur","total_icu_beds_with_ventilator":-1,"available_icu_beds_with_ventilator":-1,"hospital_phone":"9713283654, 8109793352","hospital_address":"Kotma, Madhya Pradesh 484334, India","pincode":"484334"}        """
        resources = get_bed_resources(json.loads(loaded_json_data_str))

        serialized_resources = resource_to_json(resources[1])
        expected_response = """{'resourceType': 'BED_WITH_OXYGEN', 'quantity': 6, 'total_quantity': 10}"""
        self.assertEqual(serialized_resources, expected_response)
