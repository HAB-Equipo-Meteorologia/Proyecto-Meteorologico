from src.db.db_handler import DBHandler
from fastapi import APIRouter

db = DBHandler()
router = APIRouter()

table_names = ["estaciones", "provincias", "municipios", "comunidades_autonomas"]

# Dynamic route creation
for table in table_names:
    route = f"/{table}"


    def make_route(table_name: str):
        def route_handler():
            return db.get_table_data(table_name)

        return route_handler


    router.add_api_route(route, make_route(table), methods=["GET"])

elements = ["lluvia", "temperatura", "viento", "humedad"]

for elemento in elements:
    estacion_route = f"/historico/estacion/{{idema}}/{elemento}/rango/{{fecha_ini}}/{{fecha_fin}}"
    estaciones_route = f"/historico/estaciones/{elemento}/rango/{{fecha_ini}}/{{fecha_fin}}"


    def make_estacion_route(element_name: str):
        def route_handler(idema: str, fecha_ini: str, fecha_fin: str):
            return db.get_estacion_historico(element_name, idema, fecha_ini, fecha_fin)

        return route_handler


    def make_estaciones_route(element_name: str):
        def route_handler(fecha_ini: str, fecha_fin: str):
            return db.get_estaciones_historico(element_name, fecha_ini, fecha_fin)

        return route_handler


    router.add_api_route(estacion_route, make_estacion_route(elemento), methods=["GET"])
    router.add_api_route(estaciones_route, make_estaciones_route(elemento), methods=["GET"])
