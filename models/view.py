from typing import Optional
from sqlmodel import Field, SQLModel


class View(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vin: str
    views: int = Field(default=0)
    is_hidden: bool = Field(default=False)
    is_hidden_v2: bool = Field(default=False)