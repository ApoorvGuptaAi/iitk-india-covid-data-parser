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
    BEDS = "BEDS"  # all beds, w/ or w/o oxygen
    ICUS = "ICUS"  # all icus, w/ or w/o ventilators.


@dataclass
class Resource:
    resource_type: ResourceType
    resource_description: str
    resource_qty: int  # What is available atm
    total_qty: Optional[int] = 0  # Inventory = available + unavailable


@dataclass
class Hospital:
    name: str
    address: Optional[str] = ""
    district: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""  # Required.
    location: Optional[str] = ""
    # The datetime the website entry was updated. Use time 0 if not available from the website.
    last_updated: Optional[datetime.datetime] = None
    resources: Optional[List[Resource]] = None
    debug_text: Optional[str] = None
    url: Optional[str] = None
    pincode: Optional[int] = 0
