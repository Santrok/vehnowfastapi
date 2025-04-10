from fastapi import APIRouter, Depends
import database
from models.view import View


router = APIRouter(
    prefix="/vin_view",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def get_all_items(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    query = session.query(VinViews)
    #query = query.limit(per_page).offset((page - 1) * per_page)
    #query = query.offset(page)
    res = session.execute(query)
    items = res.scalars().all()
    return items

