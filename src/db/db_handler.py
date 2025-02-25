import datetime
from typing import Optional
import psycopg2
import psycopg2.extensions
from sqlalchemy import create_engine, text, Table, MetaData
from helpers.config import get_env_var


def adapt_time(time_obj):
    return psycopg2.extensions.AsIs("'%s'::time" % time_obj.strftime('%H:%M:%S'))

psycopg2.extensions.register_adapter(datetime.time, adapt_time)

class DBHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBHandler, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(
            self,
            user: str = None,
            password: str = None,
            host: str = None,
            port: str = None,
            dbname: str = None
    ):

        try:
            self.USER = user or get_env_var("DB_USER")
            self.PASSWORD = password or get_env_var("DB_PASSWORD")
            self.HOST = host or get_env_var("DB_HOST")
            self.PORT = port or get_env_var("DB_PORT")
            self.DBNAME = dbname or get_env_var("DB_NAME")
        except KeyError as e:
            raise ValueError(f"Missing environment variable: {str(e)}")

        self.URL = f"postgresql+psycopg2://{self.USER}:{self.PASSWORD}@[{self.HOST}]:{self.PORT}/{self.DBNAME}?sslmode=require"
        self.engine = create_engine(self.URL)

    def insert_data(self, table_name: str, data: dict):
        columns = list(data.keys())
        rows = list(zip(*data.values()))
        placeholders = ", ".join([f":{col}" for col in columns])
        query = text(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})")

        with self.engine.connect() as connection:
            for row in rows:
                connection.execute(query, dict(zip(columns, row)))
            connection.commit()

    def bulk_insert_data(self, table_name: str, data: dict):
        table = Table(table_name, MetaData(), autoload_with=self.engine)
        records = []
        if data and all(isinstance(v, list) for v in data.values()):
            n_records = len(next(iter(data.values())))
            for i in range(n_records):
                record = {col: data[col][i] for col in data}
                records.append(record)

        with self.engine.begin() as connection:
            connection.execute(table.insert(), records)

    # In case of insertion mistakes, thanks to the extraction column we can easily revert back
    def delete_extracted_after_date(self, table_name: str, date_threshold):
        query = text(f"DELETE FROM {table_name} WHERE extracted >= :date_threshold")
        with self.engine.connect() as connection:
            connection.execute(query, {"date_threshold": date_threshold})
            connection.commit()

    def get_table(self, table_name: str):
        """Consulta de datos de una tabla en la base de datos"""
        query = text(f"SELECT * FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return [dict(zip(result.keys(), row)) for row in result]

    def get_schema(self, table_name: str):
        query = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = :table_name")
        with self.engine.connect() as connection:
            result = connection.execute(query, {"table_name": table_name})
            return [dict(zip(result.keys(), row)) for row in result]

    def get_columns(self, table_name: str, column_names: list):
        """Consulta de datos de una columna en la base de datos"""
        columns = ', '.join(column_names)
        query = text(f"SELECT {columns} FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            if result.rowcount == 0:
                return [{'column': col} for col in result.keys()]
            return [dict(zip(result.keys(), row)) for row in result]

    def get_estacion_historico(self, elemento: str, idema: str):
        table_name = f"{elemento}_historico"
        query = text(f"SELECT * FROM {table_name} WHERE idema = :idema")

        with self.engine.connect() as connection:
            result = connection.execute(query, {"idema": idema})
            if result.rowcount == 0:
                return [{'column': col} for col in result.keys()]
            return [dict(zip(result.keys(), row)) for row in result]

    def get_estaciones_historico(self, elemento: str):
        table_name = f"{elemento}_historico"
        query = text(f"SELECT * FROM {table_name}")

        with self.engine.connect() as connection:
            result = connection.execute(query)
            if result.rowcount == 0:
                return [{'column': col} for col in result.keys()]
            return [dict(zip(result.keys(), row)) for row in result]

    def get_estacion_historico_rango(self, elemento: str, idema: str, fechaIni: str, fechaFin: str,
                                     column_names: Optional[list] = None):
        columns = ', '.join(column_names) if column_names else '*'
        table_name = f"{elemento}_historico"
        query = text(
            f"SELECT {columns} FROM {table_name} WHERE idema = :idema AND fecha BETWEEN :fechaIni AND :fechaFin")

        with self.engine.connect() as connection:
            result = connection.execute(query, {"idema": idema, "fechaIni": fechaIni, "fechaFin": fechaFin})
            if result.rowcount == 0:
                return [{'column': col} for col in result.keys()]
            return [dict(zip(result.keys(), row)) for row in result]

    def get_estaciones_historico_rango(self, elemento: str, fechaIni: str, fechaFin: str,
                                       column_names: Optional[list] = None):
        columns = ', '.join(column_names) if column_names else '*'
        table_name = f"{elemento}_historico"
        query = text(f"SELECT {columns} FROM {table_name} WHERE fecha BETWEEN :fechaIni AND :fechaFin")

        with self.engine.connect() as connection:
            result = connection.execute(query, {"fechaIni": fechaIni, "fechaFin": fechaFin})
            if result.rowcount == 0:
                return [{'column': col} for col in result.keys()]
            return [dict(zip(result.keys(), row)) for row in result]

    def get_earliest_historical_date(self, table_name: str):
        query = text(f"SELECT MIN(fecha) FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            if result.rowcount == 0:
                return [{'column': col} for col in result.keys()]
            return result.fetchone()[0]

    def get_latest_historical_date(self, table_name: str):
        query = text(f"SELECT MAX(fecha) FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            if result.rowcount == 0:
                return [{'column': col} for col in result.keys()]
            return result.fetchone()[0]
