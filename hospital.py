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
    resource_qty: int  # What is available atm
    total_qty: Optional[int] = 0  # Inventory = available + unavailable


@dataclass
class Hospital:
    name: str
    address: str
    district: str
    city: str
    state: str  # Required.
    location: str
    last_updated: datetime
    resources: List[Resource]
    debug_text: Optional[str] = None
    url: Optional[str] = None
    pincode: Optional[int] = 0
