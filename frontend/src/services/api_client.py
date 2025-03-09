from typing import List, Optional
from common.http_request import get, post
from common.config import api_url

table_url = api_url + "/db/{table}"
historico_url = api_url + "/db/historico"
historico_earliest_url = api_url + "/db/historico/date/earliest"
historico_latest_url = api_url + "/db/historico/date/latest"
historico_avg_url = api_url + "/db/historico_average"
yearly_provincias_url = api_url + "/db/historico/yearly/provincias"
yearly_spain_url = api_url + "/db/historico/yearly/spain"
daily_url = api_url + "/db/historico/daily"
latest_fetch_url = api_url + "/db/historico/latest-fetch"
fetch_latest_url = api_url + "/db/historico/fetch-latest"

def get_table(table: str):
    return get(table_url.format(table=table))[0]

def get_historico(
        columns: Optional[List[str]] = None,
        idemas: Optional[List[str]] = None,
        fecha_ini: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        limit: Optional[int] = None
):
    params = {
        'columns': ",".join(columns) if columns else None,
        'idema': ",".join(idemas) if idemas else None,
        'fecha_ini': fecha_ini,
        'fecha_fin': fecha_fin,
        'limit': limit
    }
    print(params)
    return get(url=historico_url, params=params)[0]

def get_historico_average(
        elementos: Optional[List[str]] = None,
        provincia_ids: Optional[List[str]] = None,
        fecha_ini: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        limit: Optional[int] = None
):
    params = {
        'elementos': ",".join(elementos) if elementos else None,
        'provincia_ids': ",".join(provincia_ids) if provincia_ids else None,
        'fecha_ini': fecha_ini,
        'fecha_fin': fecha_fin,
        'limit': limit
    }
    return get(url=historico_avg_url, params=params)[0]

def get_yearly_average_provincias(
        year: int,
        elementos: Optional[List[str]] = None,
        provincia_ids: Optional[List[str]] = None
):
    params = {
        'year': year,
        'elementos': ",".join(elementos) if elementos else None,
        'provincia_ids': ",".join(provincia_ids) if provincia_ids else None
    }
    return get(url=yearly_provincias_url, params=params)[0]

def get_yearly_average_spain(
        year: int,
        elementos: Optional[List[str]] = None
):
    params = {
        'year': year,
        'elementos': ",".join(elementos) if elementos else None
    }
    return get(url=yearly_spain_url, params=params)[0]

def get_daily_average(
        elementos: Optional[List[str]] = None,
        provincia_ids: Optional[List[str]] = None,
        fecha_ini: Optional[str] = None,
        fecha_fin: Optional[str] = None
):
    params = {
        'elementos': ",".join(elementos) if elementos else None,
        'provincia_ids': ",".join(provincia_ids) if provincia_ids else None,
        'fecha_ini': fecha_ini,
        'fecha_fin': fecha_fin
    }
    return get(url=daily_url, params=params)[0]

def get_earliest_historical_date():
    return get(url=historico_earliest_url)[0]

def get_latest_historical_date():
    return get(url=historico_latest_url)[0]

def get_latest_fetch():
    return get(url=latest_fetch_url)[0][0]

def fetch_latest():
    return post(url=fetch_latest_url)[0]
