from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from urllib.parse import quote_plus
from contextlib import contextmanager
from environments.environments import Environments
from typing import List, Iterable
import pandas as pd


class Config:
    def __init__(self, engine: str, active_directory: bool = False):
        self.username = Environments.get_db_username()
        self.password = Environments.get_db_password()
        self.host_address = Environments.get_db_host()
        self.db_name = Environments.get_db_name()
        self.engine = engine
        self.active_directory = active_directory

    def get_connection_string(self) -> str:
        if self.engine == "postgres":
            return f"postgresql://{self.username}:{self.password}@{self.host_address}/{self.db_name}"
        elif self.engine in ["mssql", "sqlserver"]:
            connection_string = (
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={self.host_address};"
                f"DATABASE={self.db_name};ApplicationIntent=ReadOnly;"
            )
            if self.active_directory:
                connection_string += f"UID={self.username};Authentication=ActiveDirectoryInteractive;"
            else:
                connection_string += f"UID={self.username};PWD={self.password}"
            params = quote_plus(connection_string)
            return f"mssql+pyodbc:///?odbc_connect={params}"
        else:
            return f"sqlite:///{self.db_name}.db"

class Database:

    def __init__(self, config: Config) -> None:
        self._connection_string = config.get_connection_string()
        self._db = create_engine(self._connection_string, pool_pre_ping=True, poolclass=StaticPool)
        self._session = sessionmaker(bind=self._db)

    @contextmanager
    def session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self._session()
        try:
            yield session
        except Exception as e:
            session.rollback()
            print(f"Session rollback due to: {e}")
            raise
        finally:
            session.close()

    def get_all_from_model(self, model: object) -> List[object]:
        with self.session_scope() as session:
            return session.query(model).all()

    def get_all_from_model_with_status(self, model: object, status: List[str]) -> List[object]:
        with self.session_scope() as session:
            return session.query(model).filter(model.Status.in_(status)).all()

    def add_data_to_db(self, model: object, data: List[dict]) -> None:
        with self.session_scope() as session:
            session.bulk_insert_mappings(model, data)
            session.commit()

    def delete_row(self, model: object, id_list: List[int]) -> None:
        with self.session_scope() as session:
            for item_id in id_list:
                to_remove = session.query(model).filter_by(id=item_id).first()
                if to_remove:
                    session.delete(to_remove)
                    session.commit()

    def update_status(self, model: object, id_list: List[int], status_list: List[str]) -> None:
        """Update Status in Database"""
        with self.session_scope() as session:
            for value, sta in zip(id_list, status_list):
                try:
                    entry_to_modify = session.query(model).filter_by(id=value).first()
                    if entry_to_modify:
                        entry_to_modify.Status = sta
                except Exception as e:
                    print(f"Error updating status for ID {value}: {e}")
            session.commit()

    def query_to_dataframe(self, query_text: str, params: Iterable = None, chunksize: int = None) -> pd.DataFrame:
        """
        Run a select query against the database, returning query results as a dataframe.
        :param query_text: SQL query
        :param params: Depending on underlying SQL system, a dict, list, or tuple of params to sub into any placeholders in the query
        :param chunksize: Number of rows to read at a time
        :return: Pandas DataFrame of query result
        """
        with self.session_scope() as session:
            if chunksize:
                chunks = [chunk for chunk in pd.read_sql(query_text, session.bind, params=params, chunksize=chunksize)]
                return pd.concat(chunks) if chunks else pd.DataFrame()
            else:
                return pd.read_sql(query_text, session.bind, params=params)