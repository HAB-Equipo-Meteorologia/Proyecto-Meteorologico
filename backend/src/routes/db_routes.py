import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Query, BackgroundTasks
from backend.src.etl_scripts.pipeline import run_etl_latest
from backend.src.db.db_handler import DBHandler
from backend.src.services.resources import ResourceManager

elements = ['temperatura', 'lluvia', 'presion', 'humedad', 'viento', 'sol']

db = DBHandler()
router = APIRouter()

table_names = ["estaciones", "provincias", "comunidades_autonomas", 'historico', 'historico_avg']

res = ResourceManager()

elements_map = res.elements_map

# Dynamic route creation
for table in table_names:
    def make_table_route(table_name: str):
        def get_table(columns: Optional[str] = None):
            columns = columns.replace(' ', '') if columns else None
            columns = columns.split(',') if columns else None
            return db.get_columns(table_name, columns)

        return get_table

    def make_schema_route(table_name: str):
        def get_schema():
            return db.get_schema(table_name)

        return get_schema

    if table not in ['historico', 'historico_avg']:
        router.add_api_route(f"/table/{table}", make_table_route(table), methods=["GET"])
    router.add_api_route(f"/schema/{table}", make_schema_route(table), methods=["GET"])


elementos_query = Query(None,
    title="Elementos",
    description=f"""Elementos a mostrar separados por coma.\nValores posibles: {', '.join(elements)}""",
    alias="elementos"
)

columns_query = Query(None,
    title="Columnas",
    description="Columnas a mostrar separadas por coma. eg. idema, fecha, tmed",
    alias="columns"
)

idemas_query = Query(None,
    title="IDEMAs",
    description="IDEMAs de las estaciones a mostrar separados por coma. Ejemplos: 3129, 1387",
    alias="idema"
)

provincia_ids_query = Query(None,
    title="Provincia IDs",
    description="IDs de las provincias a mostrar separados por coma. Ejemplos: 28, 15",
    alias="provincia_id"
)

today = datetime.now().strftime('%Y-%m-%d')
last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

fecha_ini_query = Query(None,
    title="Fecha inicio",
    description=f"Fecha de inicio en formato YYYY-MM-DD. eg. {last_week}",
    alias="fecha_ini"
)

fecha_fin_query = Query(None,
    title="Fecha fin",
    description=f"Fecha de fin en formato YYYY-MM-DD. eg. {today}",
    alias="fecha_fin"
)

limit_query = Query(None,
    title="Limit",
    description="Número de registros a mostrar (seleccionados al azar). Por defecto no hay límite pero se recomienda usarlo para evitar sobrecargar el servidor.",
    alias="limit"
)

@router.get("/historico")
def get_historico(
        columns: Optional[str] = columns_query,
        idema: Optional[str] = idemas_query,
        fecha_ini: Optional[str] = fecha_ini_query,
        fecha_fin: Optional[str] = fecha_fin_query,
        limit: Optional[int] = limit_query
):

    idema = idema.replace(" ", "") if idema else None
    fecha_ini = fecha_ini.strip() if fecha_ini else None
    fecha_fin = fecha_fin.strip() if fecha_fin else None

    return db.get_historico(columns, idema, fecha_ini, fecha_fin, limit)

@router.get("/historico_average")
def get_historico_average(
        elementos: Optional[str] = elementos_query,
        provincia_ids: Optional[str] = provincia_ids_query,
        fecha_ini: Optional[str] = fecha_ini_query,
        fecha_fin: Optional[str] = fecha_fin_query,
        limit: Optional[int] = limit_query
):
    all_cols = [] if elementos else None
    if elementos:
        for element in elementos.lower().split(","):
            all_cols.extend(elements_map[element.strip()]['numeric'])
        all_cols += ["provincia_id", "fecha"]

    provincia_ids = provincia_ids.replace(" ", "") if provincia_ids else None
    fecha_ini = fecha_ini.strip() if fecha_ini else None
    fecha_fin = fecha_fin.strip() if fecha_fin else None

    return db.get_historico_average(all_cols, provincia_ids, fecha_ini, fecha_fin, limit)


@router.get("/historico/date/earliest")
def get_earliest_historical_date():
    return db.get_earliest_historical_date()

@router.get("/historico/date/latest")
def get_latest_historical_date():
    return db.get_latest_historical_date()


@router.post("/historico/fetch-latest")
async def fetch_latest_historical(background_tasks: BackgroundTasks):
    if not os.getenv("AEMET_API_KEY") and not os.getenv("AEMET_API_KEY_1"):
        return {'message': 'No AEMET API Key is present.'}
    background_tasks.add_task(run_etl_latest, origin='api')
    return {'message': 'ETL pipeline started in the background.'}

@router.get("/historico/latest-fetch")
def get_latest_fetch():
    return db.get_latest_fetch()

@router.get("/historico/yearly/provincias")
def get_yearly_average_provincias(
        year: int,
        elementos: Optional[str] = elementos_query,
        provincia_ids: Optional[str] = provincia_ids_query
):
    all_cols = [] if elementos else None
    if elementos:
        for element in elementos.lower().split(","):
            all_cols.extend(elements_map[element.strip()]['numeric'])

    provincia_ids = provincia_ids.replace(" ", "") if provincia_ids else None

    return db.get_yearly_average_provincias(year, provincia_ids, all_cols)

@router.get("/historico/yearly/spain")
def get_yearly_average(
        year: int,
        elementos: Optional[str] = elementos_query
):
    all_cols = [] if elementos else None
    if elementos:
        for element in elementos.lower().split(","):
            all_cols.extend(elements_map[element.strip()]['numeric'])

    return db.get_yearly_average_spain(year, all_cols)

@router.get("/historico/daily")
def get_daily_average(
        elementos: Optional[str] = elementos_query,
        provincia_ids: Optional[str] = provincia_ids_query,
        fecha_ini: Optional[str] = fecha_ini_query,
        fecha_fin: Optional[str] = fecha_fin_query
):
    all_cols = [] if elementos else None
    if elementos:
        for element in elementos.lower().split(","):
            all_cols.extend(elements_map[element.strip()]['numeric'])

    provincia_ids = provincia_ids.replace(" ", "") if provincia_ids else None
    fecha_ini = fecha_ini.strip() if fecha_ini else None
    fecha_fin = fecha_fin.strip() if fecha_fin else None

    return db.get_daily_average(all_cols, provincia_ids, fecha_ini, fecha_fin)

@router.get("/tables")
def all_tables():
    response = db.all_tables()
    response.sort()
    return response
