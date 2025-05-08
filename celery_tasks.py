from celery import shared_task

from sqlalchemy import text
from database import get_db_session
from logger import logger


@shared_task(bind=True, max_retries=3)
def rebuild_pagination_task(self):
    """Атомарная замена данных пагинации
    после подготовки напрямую в базе данных"""
    session = None
    try:
        session = get_db_session()

        # 1. Настройки
        session.execute(text("SET statement_timeout TO 300000"))
        session.execute(text("SET work_mem = '256MB'"))

        # 2. Создаем временные таблицы для новых данных
        session.execute(text("""
            CREATE TEMPORARY TABLE new_allcarpagination (
                LIKE allcarpagination INCLUDING ALL
            ) ON COMMIT DROP
        """))

        session.execute(text("""
            CREATE TEMPORARY TABLE new_brandcarpagination (
                LIKE brandcarpagination INCLUDING ALL
            ) ON COMMIT DROP
        """))

        # 3. Формируем новые данные во временных таблицах
        # Общая пагинация
        session.execute(text("""
            INSERT INTO new_allcarpagination (page, car_ids)
            SELECT 
                (rank - 1) / 10 + 1 AS page_num,
                array_agg(id ORDER BY id DESC)
            FROM (
                SELECT 
                    id,
                    ROW_NUMBER() OVER (ORDER BY id DESC) AS rank
                FROM car
                WHERE is_hidden = FALSE
            ) t
            GROUP BY (rank - 1) / 10
            ORDER BY page_num
        """))

        # Пагинация по брендам
        session.execute(text("""
            INSERT INTO new_brandcarpagination (brand, brand_id, page_num, car_ids)
            SELECT 
                brand,
                brand_id,
                (rank - 1) / 10 + 1 AS page_num,
                array_agg(id ORDER BY id DESC)
            FROM (
                SELECT 
                    c.id,
                    c.brand,
                    cb.id AS brand_id,
                    ROW_NUMBER() OVER (PARTITION BY c.brand ORDER BY c.id DESC) AS rank
                FROM car c
                JOIN carbrand cb ON c.brand = cb.name
                WHERE c.is_hidden = FALSE
                ORDER BY c.brand, c.id DESC
            ) t
            GROUP BY brand, brand_id, (rank - 1) / 10
            ORDER BY brand, page_num
        """))

        # 4. Атомарная замена данных (в одной транзакции)
        with session.begin_nested():
            # Очищаем основные таблицы
            session.execute(text("TRUNCATE TABLE allcarpagination CONTINUE IDENTITY"))
            session.execute(text("TRUNCATE TABLE brandcarpagination CONTINUE IDENTITY"))

            # Копируем новые данные
            session.execute(text("""
                INSERT INTO allcarpagination 
                SELECT * FROM new_allcarpagination
            """))

            session.execute(text("""
                INSERT INTO brandcarpagination 
                SELECT * FROM new_brandcarpagination
            """))

        # 5. Проверка результатов
        stats = session.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM allcarpagination) as global_pages,
                (SELECT COUNT(*) FROM brandcarpagination) as brand_pages,
                (SELECT COUNT(DISTINCT brand_id) FROM brandcarpagination) as brands_count
        """)).fetchone()

        session.commit()
        logger.info("Пересчет пагинации v1 выполнен успешно")
        return {
            "status": "pagination v1 is success",
            "global_pages": stats.global_pages,
            "brand_pages": stats.brand_pages,
            "brands_count": stats.brands_count
        }

    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"Ошибка пересчета пагинации: {str(e)}")
        self.retry(exc=e, countdown=120)
    finally:
        if session:
            try:
                session.execute(text("RESET statement_timeout"))
                session.execute(text("RESET work_mem"))
                session.close()
            except Exception:
                pass


@shared_task(bind=True, max_retries=3)
def rebuild_pagination_task_v2(self):
    """Атомарная замена данных пагинации
    после подготовки напрямую в базе данных"""
    session = None
    try:
        session = get_db_session()

        # 1. Настройки
        session.execute(text("SET statement_timeout TO 300000"))
        session.execute(text("SET work_mem = '256MB'"))

        # 2. Создаем временные таблицы для новых данных
        session.execute(text("""
            CREATE TEMPORARY TABLE new_allcarpagination2 (
                LIKE allcarpagination2 INCLUDING ALL
            ) ON COMMIT DROP
        """))

        session.execute(text("""
            CREATE TEMPORARY TABLE new_brandcarpagination2 (
                LIKE brandcarpagination2 INCLUDING ALL
            ) ON COMMIT DROP
        """))

        # 3. Формируем новые данные во временных таблицах
        # Общая пагинация
        session.execute(text("""
            INSERT INTO new_allcarpagination2 (page, car_ids)
            SELECT 
                (rank - 1) / 10 + 1 AS page_num,
                array_agg(id ORDER BY id DESC)
            FROM (
                SELECT 
                    id,
                    ROW_NUMBER() OVER (ORDER BY id DESC) AS rank
                FROM car
                WHERE is_hidden_v2 = FALSE
            ) t
            GROUP BY (rank - 1) / 10
            ORDER BY page_num
        """))

        # Пагинация по брендам
        session.execute(text("""
            INSERT INTO new_brandcarpagination2 (brand, brand_id, page_num, car_ids)
            SELECT 
                brand,
                brand_id,
                (rank - 1) / 10 + 1 AS page_num,
                array_agg(id ORDER BY id DESC)
            FROM (
                SELECT 
                    c.id,
                    c.brand,
                    cb.id AS brand_id,
                    ROW_NUMBER() OVER (PARTITION BY c.brand ORDER BY c.id DESC) AS rank
                FROM car c
                JOIN carbrand cb ON c.brand = cb.name
                WHERE c.is_hidden_v2 = FALSE
                ORDER BY c.brand, c.id DESC
            ) t
            GROUP BY brand, brand_id, (rank - 1) / 10
            ORDER BY brand, page_num
        """))

        # 4. Атомарная замена данных (в одной транзакции)
        with session.begin_nested():
            # Очищаем основные таблицы
            session.execute(text("TRUNCATE TABLE allcarpagination2 CONTINUE IDENTITY"))
            session.execute(text("TRUNCATE TABLE brandcarpagination2 CONTINUE IDENTITY"))

            # Копируем новые данные
            session.execute(text("""
                INSERT INTO allcarpagination2 
                SELECT * FROM new_allcarpagination2
            """))

            session.execute(text("""
                INSERT INTO brandcarpagination2 
                SELECT * FROM new_brandcarpagination2
            """))

        # 5. Проверка результатов
        stats = session.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM allcarpagination2) as global_pages,
                (SELECT COUNT(*) FROM brandcarpagination2) as brand_pages,
                (SELECT COUNT(DISTINCT brand_id) FROM brandcarpagination2) as brands_count
        """)).fetchone()

        session.commit()
        logger.info("Пересчет пагинации v2 выполнен успешно")
        return {
            "status": "pagination-v2 is success",
            "global_pages": stats.global_pages,
            "brand_pages": stats.brand_pages,
            "brands_count": stats.brands_count
        }

    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"Ошибка пересчета пагинации v2: {str(e)}")
        self.retry(exc=e, countdown=120)
    finally:
        if session:
            try:
                session.execute(text("RESET statement_timeout"))
                session.execute(text("RESET work_mem"))
                session.close()
            except Exception:
                pass