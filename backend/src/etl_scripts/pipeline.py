import time
import os
from datetime import datetime, timedelta, date
import pandas as pd
from common.logger import setup_logger
from backend.src.etl_scripts.cleaning import clean_historical, sort_historico_avg
from backend.src.services.helpers import provincia_avg
from backend.src.etl_scripts.uploading import insert_batches
from backend.src.etl_scripts.extraction import extract_historical_data
from backend.src.clients.supabase_client import SupabaseClient
from backend.src.db.db_handler import DBHandler

script_dir = os.path.dirname(__file__)

logger = setup_logger("etl_pipeline")

def filter_date_range(start_date, end_date):
    db = DBHandler()

    year = start_date.year

    db_earliest_date = db.get_earliest_historical_date(year)
    db_latest_date = db.get_latest_historical_date(year)

    if end_date < db_earliest_date or start_date > db_latest_date:
        logger.info("Requested date range is outside existing data. Processing full range.")
        return start_date, end_date

    new_start_date = start_date
    new_end_date = end_date

    # Adjust start_date to latest + 1
    if db_earliest_date <= start_date <= db_latest_date:
        new_start_date = db_latest_date + timedelta(days=1)
        logger.info(f"Start date adjusted to {new_start_date} (after latest DB date)")

    # Adjust end_date to earliest -1
    if db_earliest_date <= end_date <= db_latest_date:
        new_end_date = db_earliest_date - timedelta(days=1)
        logger.info(f"End date adjusted to {new_end_date} (before earliest DB date)")

    if new_start_date > new_end_date:
        return None, None

    logger.info(f"Processing filtered date range: {new_start_date} to {new_end_date}")
    return new_start_date, new_end_date

async def run_etl(start_date: date, end_date: date):

    if start_date.year != end_date.year:
        message = "Start and end date must be in the same year. To process multiple years, run ETL for each year separately."
        logger.error(message)
        return message, False

    logger.info(f"Running ETL for date range {start_date} to {end_date}...")

    db = DBHandler()

    if db.table_exists(f'historico_{start_date.year}') and not db.is_empty(f'historico_{start_date.year}'):
        start_date, end_date = filter_date_range(start_date, end_date)
        if start_date is None:
            message = "No new data to process after filtering existing date range"
            logger.info(message)
            return message, False

    data = await extract_historical_data(start_date, end_date)

    if data is None or len(data) == 0:
        message = "No data was extracted."
        logger.warning(message)
        return message, False

    df = pd.DataFrame(data)

    df = clean_historical(df)
    avg_df = provincia_avg(df)

    start_date = datetime.strptime(df['fecha'].min(), "%Y-%m-%d")
    end_date = datetime.strptime(df['fecha'].max(), "%Y-%m-%d")

    year = start_date.year

    start_time = time.time()
    logger.info(f"Uploading historical data for date range {start_date.date()} to {end_date.date()}...")

    if not db.table_exists(f'historico_{year}'):
        db.create_historical_table(year)

    table = f"historico_{year}"
    logger.info(f"Uploading historico_{year}...")
    insert_batches(table, df)

    logger.info("Uploading historico_avg...")
    insert_batches('historico_avg', avg_df)

    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time for all tables: {elapsed_time:.2f} seconds")

    historico_path = os.path.join(script_dir, '../data/historical/historico')
    avg_path = os.path.join(script_dir, '../data/historical/historico_avg')

    os.makedirs(historico_path, exist_ok=True)
    os.makedirs(avg_path, exist_ok=True)

    historico_path = os.path.join(historico_path, f'{year}.csv')
    avg_path = os.path.join(avg_path, f'{year}.csv')

    if not os.path.exists(historico_path):
        # no data for this year yet
        df.to_csv(historico_path, index=False)
        avg_df.to_csv(avg_path, index=False)
    else:
        # append to existing data
        df.to_csv(historico_path, mode='a', header=False, index=False)
        avg_df.to_csv(avg_path, mode='a', header=False, index=False)

    message = "ETL process completed."
    logger.info(message)
    return message, True

async def run_etl_latest(origin: str):
    logger.info("Running ETL Latest...")

    db = DBHandler()
    current_latest = db.get_latest_historical_date()
    logger.info(f"Current latest: {current_latest}")
    start_date = current_latest + timedelta(days=1)
    end_date = datetime.now().date()

    try:
        msg, new = await run_etl(start_date, end_date)
        failure = False
    except Exception as e:
        msg, new = str(e), False
        failure = True

    db.update_latest_fetch(origin, new, failure, msg)

    status = 500 if failure else 200
    return msg, status

async def extract_year(year: int):

    start = date(year=year, month=1, day=1)
    end = date(year=year, month=6, day=28)  # inclusive

    await run_etl(start, end)

    start = date(year=year, month=6, day=29)
    end = date(year=year, month=12, day=31)  # inclusive

    await run_etl(start, end)

    sort_historico_avg(year)

    sb = SupabaseClient()

    historico_path = os.path.join(script_dir, f'../data/historical/historico/{year}.csv')
    avg_path = os.path.join(script_dir, f'../data/historical/historico_avg/{year}.csv')

    sb.upload_file(historico_path, 'historical', f"historico/{year}.csv")
    sb.upload_file(avg_path, 'historical', f"historico_avg/{year}.csv")
