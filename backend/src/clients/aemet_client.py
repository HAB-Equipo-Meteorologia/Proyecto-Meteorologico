import json
import os

import aiohttp
from common.http_request import get_async
from common.logger import setup_logger


def _format_fecha(fecha: str):
    return f"{fecha}T00:00:00UTC"


class AEMETClient:
    BASE_URL = "https://opendata.aemet.es/opendata/api"

    ENDPOINTS = {
        'maestro': {
            'municipio': '/maestro/municipio/{municipio_id}'
        },
        'observacion-convencional': {
            'tiempo-actual': '/observacion/convencional/todas',
            'tiempo-actual-estacion': '/observacion/convencional/datos/estacion/{idema}'
        },
        'predicciones-especificas': {
            'municipio-horaria': '/prediccion/especifica/municipio/horaria/{municipio}'
        },
        'valores-climatologicos': {
            'estacion-diaria': '/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}',
            'estaciones-diaria': '/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/todasestaciones'
        }
    }

    _instance = None
    _api_key = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AEMETClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.logger = setup_logger("aemet_client")

        self.cycle_api_key = os.getenv("AEMET_API_KEY_1") is not None
        self.logger.info(f"Cycle API Key: {self.cycle_api_key}")

        self.num_keys = 1
        self.current_key = 1

        if self.cycle_api_key:
            while os.getenv(f"AEMET_API_KEY_{self.num_keys + 1}") is not None:
                self.num_keys += 1
            self.logger.info(f"Number of API keys: {self.num_keys}")

        api_key = os.getenv(f"AEMET_API_KEY_{self.current_key}") \
            if self.cycle_api_key else os.getenv("AEMET_API_KEY")

        self._set_api_key(api_key)

    def _set_api_key(self, api_key: str):
        self._api_key = api_key

    def _headers(self):
        return {'api_key': self._api_key}

    def _cycle_api_key(self):
        if self.cycle_api_key:
            self.current_key = (self.current_key % self.num_keys) + 1
            self._set_api_key(os.getenv(f"AEMET_API_KEY_{self.current_key}"))

    async def _make_request(self, session: aiohttp.ClientSession, endpoint: str, attempt=1, **kwargs):
        url = self.BASE_URL + endpoint.format(**kwargs)
        self.logger.info(f"Making request to {url}")

        try:
            response = await get_async(url=url, session=session, headers=self._headers())
            self.logger.info(f"Response: {response}")

        except Exception as e:
            self.logger.error(f"Error in request: {e}")
            if attempt <= self.num_keys:  # This will try all keys before failing
                self.logger.info(f"Trying with next API key...")
                self._cycle_api_key()
                return await self._make_request(session, endpoint, attempt+1, **kwargs)
            else:
                raise e

        if response[0]['estado'] == 404:
            return None

        datos = await get_async(url=response[0]['datos'], session=session, headers=self._headers())

        return json.loads(datos[0])

    async def get_estacion_data(self, session, idema: str):
        endpoint = self.ENDPOINTS['observacion-convencional']['tiempo-actual']
        return await self._make_request(session, endpoint.format(idema=idema))

    async def get_municipio(self, session, municipio_id: str):
        endpoint = self.ENDPOINTS['maestro']['municipio']
        return await self._make_request(session, endpoint, municipio_id=municipio_id)

    async def get_historico_estacion(self, session, fechaIniStr: str, fechaFinStr: str, idema: str):
        endpoint = self.ENDPOINTS['valores-climatologicos']['estacion-diaria']
        return await self._make_request(session, endpoint, fechaIniStr=_format_fecha(fechaIniStr),
                                            fechaFinStr=_format_fecha(fechaFinStr), idema=idema)

    async def get_historico_todas_estaciones(self, session, fechaIniStr: str, fechaFinStr: str):
        endpoint = self.ENDPOINTS['valores-climatologicos']['estaciones-diaria']
        return await self._make_request(session, endpoint, fechaIniStr=_format_fecha(fechaIniStr),
                                            fechaFinStr=_format_fecha(fechaFinStr))

    async def get_tiempo_actual(self, session):
        endpoint = self.ENDPOINTS['observacion-convencional']['tiempo-actual']
        return await self._make_request(session, endpoint)

    async def get_tiempo_actual_estacion(self, session, idema: str):
        endpoint = self.ENDPOINTS['observacion-convencional']['tiempo-actual-estacion']
        return await self._make_request(session, endpoint.format(idema=idema))
