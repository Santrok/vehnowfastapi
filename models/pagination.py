from typing import List, Optional
from sqlmodel import SQLModel, Field


class AllCarPagination(SQLModel, table=True):
    """
    Модель для хранения пагинированных данных об автомобилях v1.
    Содержит информацию о распределении автомобилей по страницам.

    Attributes:
        id (Optional[int]): Уникальный идентификатор записи (автоинкремент)
        page (Optional[int]): Номер страницы пагинации (начиная с 1)
        car_ids (Optional[List[int]]): Список ID автомобилей на странице,
                                          отсортированный в порядке отображения

    Notes:
        - Данные заполняются автоматически в задаче пересчета пагинации
    """
    id: Optional[int] = Field(primary_key=True)
    page: Optional[int] = Field(default=None)
    car_ids: Optional[List[int]] = Field(default=None, nullable=True)


class BrandCarPagination(SQLModel, table=True):
    """
    Модель для хранения пагинированных данных об автомобилях по брендам v1.
    Оптимизирована для быстрого доступа к спискам автомобилей по брендам и страницам.

    Attributes:
        id (Optional[int]): Первичный ключ, автоинкрементный идентификатор записи.
                           Пример: 1
        brand (str): Название бренда (должно соответствовать таблице брендов).
                    Пример: "Toyota"
        brand_id (int): Внешний ключ на таблицу carbrand.
                       Пример: 42
        page_num (int): Номер страницы пагинации (начиная с 1).
                       Пример: 3
        car_ids (List[int]): Массив ID автомобилей на странице, отсортированный
                           в порядке отображения (по убыванию ID).
                           Пример: [1523, 1520, 1518]

    Notes:
        - Данные заполняются автоматически в задаче пересчета пагинации

    """
    id: Optional[int] = Field(default=None, primary_key=True)
    brand: str = Field(index=True)
    brand_id: int = Field(index=True)
    page_num: int = Field(index=True)
    car_ids: List[int] = Field(default=None, nullable=True)


class AllCarPagination2(SQLModel, table=True):
    """
    Модель для хранения пагинированных данных об автомобилях v2.
    Содержит информацию о распределении автомобилей по страницам.

    Attributes:
        id (Optional[int]): Уникальный идентификатор записи (автоинкремент)
        page (Optional[int]): Номер страницы пагинации (начиная с 1)
        car_ids (Optional[List[int]]): Список ID автомобилей на странице,
                                          отсортированный в порядке отображения

    Notes:
        - Данные заполняются автоматически в задаче пересчета пагинации
    """
    id: Optional[int] = Field(primary_key=True)
    page: Optional[int] = Field(default=None)
    car_ids: Optional[List[int]] = Field(default=None, nullable=True)


class BrandCarPagination2(SQLModel, table=True):
    """
    Модель для хранения пагинированных данных об автомобилях по брендам v1.
    Оптимизирована для быстрого доступа к спискам автомобилей по брендам и страницам.

    Attributes:
        id (Optional[int]): Первичный ключ, автоинкрементный идентификатор записи.
                           Пример: 1
        brand (str): Название бренда (должно соответствовать таблице брендов).
                    Пример: "Toyota"
        brand_id (int): Внешний ключ на таблицу carbrand.
                       Пример: 42
        page_num (int): Номер страницы пагинации (начиная с 1).
                       Пример: 3
        car_ids (List[int]): Массив ID автомобилей на странице, отсортированный
                           в порядке отображения (по убыванию ID).
                           Пример: [1523, 1520, 1518]

    Notes:
        - Данные заполняются автоматически в задаче пересчета пагинации

    """
    id: Optional[int] = Field(default=None, primary_key=True)
    brand: str = Field(index=True)
    brand_id: int = Field(index=True)
    page_num: int = Field(index=True)
    car_ids: List[int] = Field(default=None, nullable=True)