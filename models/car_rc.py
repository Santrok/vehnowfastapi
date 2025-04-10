from typing import Optional, List
from sqlmodel import Field, SQLModel


class CarRc(SQLModel, table=True): #allowed only 20 for apiv1 and 20 for apiv2
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int = Field(default=None)
    brand: str = Field(default=None)
    model: str = Field(default=None)
    vin: str = Field(default=None)
    odometer: str = Field(default=None)
    engine: str = Field(default=None)
    gearbox: str = Field(default=None)
    drive_train: str = Field(default=None)
    auction_date: str = Field(default=None)
    sale_type: str = Field(default=None)
    damage: str = Field(default=None)
    photo: List[str] = Field(default=None)
    is_hidden: bool = Field(default=False)

    apiv1: bool = Field(default=True) #got from apiv1 if true, otherwise from apiv2, can be hidden from is_hidden for specific api in this value