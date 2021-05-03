from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import datetime


# Resource type defined at https://github.com/abhinavj13/iitk-covid-help-api/blob/master/src/services/dataLead/db/enum.ts
class ResourceType(Enum):
    BED_WITHOUT_OXYGEN = "BED_WITHOUT_OXYGEN"
    BED_WITH_OXYGEN = "BED_WITH_OXYGEN"
    ICU_WITH_VENTILATOR = "ICU_WITH_VENTILATOR"
    ICU_WITHOUT_VENTILATOR = "ICU_WITHOUT_VENTILATOR"
    BEDS = "BEDS"
    ICUS = "ICUS"


@dataclass
class Resource:
    resource_type: ResourceType
    resource_description: str
    resource_qty: int
    total_qty: Optional[int] = 0


@dataclass
class Hospital:
    name: str
    address: str
    district: str
    city: str
    state: str
    location: str
    last_updated: datetime
    resources: List[Resource]


def map_raw_resource_str_to_type(resource_str: str) -> ResourceType:
    if resource_str == "available_beds_allocated_to_covid":
        return ResourceType.BEDS
    if resource_str == "available_beds_without_oxygen":
        return ResourceType.BED_WITHOUT_OXYGEN
    if resource_str == "available_beds_with_oxygen":
        return ResourceType.BED_WITH_OXYGEN
    if resource_str == "available_icu_beds_with_ventilator":
        return ResourceType.ICU_WITH_VENTILATOR
    if resource_str == "available_icu_beds_without_ventilator":
        return ResourceType.ICU_WITHOUT_VENTILATOR
    return None