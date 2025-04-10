from typing import Optional, List
from sqlmodel import Field, SQLModel


class Vv1(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vin: str = Field(default=None)

    views: int = Field(default=0)
 #got from apiv1 if true, otherwise from apiv2, can be hidden from is_hidden for specific api in this value