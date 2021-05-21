from hospital import Hospital
from typing import List
from abc import abstractmethod


class HtmlHospitalParser:

    @abstractmethod
    def parse_hospitals(self):
        pass
