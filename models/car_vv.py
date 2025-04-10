from typing import Optional, List
from sqlmodel import Field, SQLModel


class CarVv(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    brand: str = Field(default=None)
    model: str = Field(default=None)
    vin: str = Field(default=None)
    views: int = Field(default=0)
    is_hidden: bool = Field(default=False)
    is_hidden_v2: bool = Field(default=False)