from sqlalchemy import create_engine, text
from helpers.config import get_env_var


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
        """Inserta datos en una tabla de la base de datos"""
        columns = ', '.join(data.keys())
        values = ', '.join(f':{key}' for key in data.keys())
        query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")

        with self.engine.connect() as connection:
            connection.execute(query, data)
            connection.commit()

    def get_table_data(self, table_name: str):
        """Consulta de datos de una tabla en la base de datos"""
        query = text(f"SELECT * FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return [dict(zip(result.keys(), row)) for row in result]

    def get_estacion_historico(self, elemento: str, idema: str, fechaIni: str, fechaFin: str):
        table_name = f"{elemento}_historico"
        query = text(f"SELECT * FROM {table_name} WHERE idema = :idema AND fecha BETWEEN :fechaIni AND :fechaFin")

        with self.engine.connect() as connection:
            result = connection.execute(query, {"idema": idema, "fechaIni": fechaIni, "fechaFin": fechaFin})
            return [dict(zip(result.keys(), row)) for row in result]

    def get_estaciones_historico(self, elemento: str, fechaIni: str, fechaFin: str):
        table_name = f"{elemento}_historico"
        query = text(f"SELECT * FROM {table_name} WHERE fecha BETWEEN :fechaIni AND :fechaFin")

        with self.engine.connect() as connection:
            result = connection.execute(query, {"fechaIni": fechaIni, "fechaFin": fechaFin})
            return [dict(zip(result.keys(), row)) for row in result]

    def get_earliest_historical_date(self, table_name: str):
        query = text(f"SELECT MIN(fecha) FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchone()[0]

    def get_latest_historical_date(self, table_name: str):
        query = text(f"SELECT MAX(fecha) FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchone()[0]
