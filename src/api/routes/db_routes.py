from fastapi import APIRouter
from src.db.db_handler import DBHandler

db = DBHandler()
router = APIRouter()

table_names = ["estaciones", "provincias", "comunidades_autonomas"]

# Dynamic route creation
for table in table_names:
    def make_table_route(table_name: str):
        def route_handler():
            return db.get_table(table_name)

        return route_handler


    def make_columns_route(table_name: str):
        def route_handler(columns: str):
            return db.get_columns(table_name, columns.split(","))

        return route_handler


    router.add_api_route(f"/{table}", make_table_route(table), methods=["GET"])
    router.add_api_route(f"/{table}/columns", make_columns_route(table), methods=["GET"])

elements = ["lluvia", "temperatura", "viento", "humedad"]

estacion_route = f"/historico/estacion/{{idema}}/{{elemento}}"
estaciones_route = f"/historico/estaciones/{{elemento}}"
estacion_rango_route = f"/historico/estacion/{{idema}}/{{elemento}}/rango/{{fecha_ini}}/{{fecha_fin}}"
estaciones_rango_route = f"/historico/estaciones/{{elemento}}/rango/{{fecha_ini}}/{{fecha_fin}}"


def make_estacion_rango_route():
    def route_handler(idema: str, fecha_ini: str, fecha_fin: str, elemento: str):
        return db.get_estacion_historico_rango(elemento, idema, fecha_ini, fecha_fin)

    return route_handler


def make_estaciones_rango_route():
    def route_handler(fecha_ini: str, fecha_fin: str, elemento: str):
        return db.get_estaciones_historico_rango(elemento, fecha_ini, fecha_fin)

    return route_handler


def make_estacion_route():
    def route_handler(idema: str, elemento: str):
        return db.get_estacion_historico(elemento, idema)

    return route_handler


def make_estaciones_route():
    def route_handler(elemento: str):
        return db.get_estaciones_historico(elemento)

    return route_handler


router.add_api_route(estacion_route, make_estacion_route(), methods=["GET"])
router.add_api_route(estaciones_route, make_estaciones_route(), methods=["GET"])
router.add_api_route(estacion_rango_route, make_estacion_rango_route(), methods=["GET"])
router.add_api_route(estaciones_rango_route, make_estaciones_rango_route(), methods=["GET"])
