from hospital import Hospital
from typing import List
from abc import abstractmethod


class HtmlHospitalParser:
    @abstractmethod
    def read_page(self):
        pass

    @abstractmethod
    def parse_hospitals(self) -> List[Hospital]:
        pass
