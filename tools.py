import database
from sqlmodel import text

class Tools:
    @staticmethod
    def count_query_row(query: str, session: database.Session):
        query_str = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        return session.execute(text("SELECT row_estimator(:query_str)"), {"query_str": query_str}).scalar()