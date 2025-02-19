from helpers import http_request
from helpers.config import api_url
from helpers.http_request import make_request

api_endpoints = {
    "table": "/db/{table}",
    "estacion": "/db/historico/estacion/{idema}/{elemento}/rango/{fecha_ini}/{fecha_fin}",
    "estaciones": "/db/historico/estaciones/{elemento}/rango/{fecha_ini}/{fecha_fin}"
}


def get_table(table: str):
    url = api_url + api_endpoints['table'].format(table=table)
    return make_request(method='get', url=url)[0]


def get_estacion_historico(idema: str, elemento: str, fecha_ini: str, fecha_fin: str):
    url = api_url + api_endpoints['estacion'].format(
        idema=idema,
        elemento=elemento,
        fecha_ini=fecha_ini,
        fecha_fin=fecha_fin)
    return http_request.make_request(method='get', url=url)[0]


def get_estaciones_historico(elemento: str, fecha_ini: str, fecha_fin: str):
    url = api_url + api_endpoints['estaciones'].format(
        elemento=elemento,
        fecha_ini=fecha_ini,
        fecha_fin=fecha_fin)
    return http_request.make_request(method='get', url=url)[0]
