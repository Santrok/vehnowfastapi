from fastapi import APIRouter, Depends
import database
from models.car_model import CarModel


router = APIRouter(
    prefix="/model",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{brand}/")
def get_all_items(brand: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    query = session.query(CarModel).filter(CarModel.brand == brand)
    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()
    return items

