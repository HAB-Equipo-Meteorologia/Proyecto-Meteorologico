import json
import aiohttp
from helpers.http_request import get_async


def _format_fecha(fecha: str):
    return f"{fecha}T00:00:00UTC"


class AEMETClient:
    BASE_URL = "https://opendata.aemet.es/opendata/api"

    ENDPOINTS = {
        'maestro': {
            'municipio': '/maestro/municipio/{municipio_id}'
        },
        'observacion-convencional': {
            'tiempo-actual': '/observacion/convencional/datos/estacion/{idema}'
        },
        'predicciones-especificas': {
            'municipio-horaria': '/prediccion/especifica/municipio/horaria/{municipio}'
        },
        'valores-climatologicos': {
            'estacion-diaria': '/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}',
            'estaciones-diaria': '/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones'
        }
    }

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._headers = {'api_key': api_key}

    async def _make_request(self, endpoint: str, **kwargs):
        url = self.BASE_URL + endpoint.format(**kwargs)

        async with aiohttp.ClientSession() as session:
            response = await get_async(url=url, session=session, headers=self._headers)

            datos = await get_async(url=response[0]['datos'], session=session, headers=self._headers)
            metadatos = await get_async(url=response[0]['metadatos'], session=session, headers=self._headers)

            return {
                'datos': datos,
                'metadatos': metadatos
            }

    async def get_predicciones_municipio(self, municipio: str):
        endpoint = self.ENDPOINTS['predicciones-especificas']['municipio-horaria']
        response = await self._make_request(endpoint.format(municipio=municipio))

        return json.loads(response['datos'][0])[0]['prediccion']['dia']

    async def get_estacion_data(self, idema: str):
        endpoint = self.ENDPOINTS['observacion-convencional']['tiempo-actual']
        response = await self._make_request(endpoint.format(idema=idema))

        return json.loads(response['datos'][0])

    async def get_municipio(self, municipio_id: str):
        endpoint = self.ENDPOINTS['maestro']['municipio']
        response = await self._make_request(endpoint, municipio_id=municipio_id)

        return json.loads(response['datos'][0])

    async def get_valores_climatologicos_diarios_estacion(self, fechaIniStr: str, fechaFinStr: str, idema: str):
        endpoint = self.ENDPOINTS['valores-climatologicos']['estacion-diaria']
        response = await self._make_request(endpoint, fechaIniStr=_format_fecha(fechaIniStr),
                                            fechaFinStr=_format_fecha(fechaFinStr), idema=idema)

        return json.loads(response['datos'][0])

    async def get_valores_climatologicos_diarios_todas_estaciones(self, fechaIniStr: str, fechaFinStr: str):
        endpoint = self.ENDPOINTS['valores-climatologicos']['estaciones-diaria']
        response = await self._make_request(endpoint, fechaIniStr=_format_fecha(fechaIniStr),
                                            fechaFinStr=_format_fecha(fechaFinStr))

        return json.loads(response['datos'][0])
