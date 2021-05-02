@dataclass
class Resource:
  resource_type: str    # Resource type defined at https://github.com/abhinavj13/iitk-covid-help-api/blob/master/src/services/dataLead/db/enum.ts   
  resource_description: str
  resource_qty: int

@dataclass
class Hospital:
  name: str
  address: str
  district: str
  city: str
  state: str
  beds_text: str
  location: str
  ventilator: int
  last_updated: datetime
  resources: List[Resource]
