from typing import Optional, List
from sqlmodel import Field, SQLModel


class Car(SQLModel, table=True):
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
    is_hidden_v2: bool = Field(default=False)
    brand_id: int = Field(default=None)