from typing import List
from fastapi import APIRouter
from sqlalchemy.orm import Query
from src.db.db_handler import DBHandler

db = DBHandler()
router = APIRouter()

table_names = ["estaciones", "provincias", "municipios", "comunidades_autonomas"]

# Dynamic route creation
for table in table_names:
    def make_table_route(table_name: str):
        def route_handler():
            return db.get_table_data(table_name)

        return route_handler


    def make_column_route(table_name: str, column_name: str):
        def route_handler():
            return db.get_column(table_name, column_name)

        return route_handler


    def make_columns_route(table_name: str):
        def route_handler(columns: List[str] = Query(...)):
            return db.get_columns(table_name, columns)

        return route_handler


    router.add_api_route(f"/{table}", make_table_route(table), methods=["GET"])
    router.add_api_route(f"/{table}/{{column_name}}", make_column_route(table, "{column_name}"), methods=["GET"])
    router.add_api_route(f"/{table}/columns", make_columns_route(table), methods=["GET"])

elements = ["lluvia", "temperatura", "viento", "humedad"]

for elemento in elements:
    estacion_route = f"/historico/estacion/{{idema}}/{elemento}"
    estaciones_route = f"/historico/estaciones/{elemento}"
    estacion_rango_route = f"/historico/estacion/{{idema}}/{elemento}/rango/{{fecha_ini}}/{{fecha_fin}}"
    estaciones_rango_route = f"/historico/estaciones/{elemento}/rango/{{fecha_ini}}/{{fecha_fin}}"


    def make_estacion_rango_route(element_name: str):
        def route_handler(idema: str, fecha_ini: str, fecha_fin: str):
            return db.get_estacion_historico_rango(element_name, idema, fecha_ini, fecha_fin)

        return route_handler


    def make_estaciones_rango_route(element_name: str):
        def route_handler(fecha_ini: str, fecha_fin: str):
            return db.get_estaciones_historico_rango(element_name, fecha_ini, fecha_fin)

        return route_handler


    def make_estacion_route(element_name: str):
        def route_handler(idema: str):
            return db.get_estacion_historico(element_name, idema)

        return route_handler


    def make_estaciones_route(element_name: str):
        def route_handler():
            return db.get_estaciones_historico(element_name)

        return route_handler


    router.add_api_route(estacion_route, make_estacion_route(elemento), methods=["GET"])
    router.add_api_route(estaciones_route, make_estaciones_route(elemento), methods=["GET"])
    router.add_api_route(estacion_rango_route, make_estacion_rango_route(elemento), methods=["GET"])
    router.add_api_route(estaciones_rango_route, make_estaciones_rango_route(elemento), methods=["GET"])
