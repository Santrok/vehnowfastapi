from fastapi import APIRouter, Depends
import database
from models.car_brand import CarBrand


router = APIRouter(
    prefix="/brand",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def get_all_items(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    query = session.query(CarBrand)
    #query = query.limit(per_page).offset((page - 1) * per_page)
    #query = query.offset(page)
    res = session.execute(query)
    items = res.scalars().all()
    return items


