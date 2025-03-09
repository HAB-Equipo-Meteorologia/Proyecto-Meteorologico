import asyncio
from datetime import datetime, timedelta, date
import aiohttp
from backend.src.clients.aemet_client import AEMETClient
from common.logger import setup_logger


logger = setup_logger("etl_extraction")

client = AEMETClient()

async def extract_historical_data(
        start_date: date,
        end_date: date,
        delay: int = 2
):

    current_start_date = start_date
    end_date = min(datetime.now().date(), end_date)
    all_data = []

    async with aiohttp.ClientSession() as session:
        while current_start_date <= end_date:

            current_end_date = current_start_date + timedelta(days=14)
            current_end_date = min(end_date, current_end_date)

            start_date = current_start_date.strftime("%Y-%m-%d")
            current_end_date = current_end_date.strftime("%Y-%m-%d")

            logger.info(f"Fetching data for date range {start_date} to {current_end_date}...")

            try:
                # noinspection PyUnresolvedReferences
                data = await client.get_historico_todas_estaciones(session, start_date, current_end_date)

                if data is not None:
                    all_data.extend(data)
                    logger.info(f"Retrieved data for date range {start_date} to {current_end_date}")
                else:
                    return None

                current_start_date += timedelta(days=15)  # Max batches of 15 days
                await asyncio.sleep(delay)

            except ValueError as e:
                logger.error(e)
                raise e

            except Exception as e:
                logger.error(e, e.args)

    return all_data


async def extract_live_data():

    logger.info("Fetching live data...")

    async with aiohttp.ClientSession() as session:

        try:
            data = await client.get_tiempo_actual(session)

            if data is not None:
                logger.info("Retrieved live data")
                return data
            else:
                raise ValueError("Data is None")

        except ValueError as e:
            logger.error(e)
            return None

        except Exception as e:
            logger.error(e, e.args)

    return None