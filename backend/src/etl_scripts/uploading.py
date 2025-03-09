import time
from common.logger import setup_logger
from backend.src.db.db_handler import DBHandler

logger = setup_logger("etl_uploading")

def insert_batches(table, df, batch_size=10000):
    logger.info(f"Inserting batches of {batch_size} records...")
    start_time = time.time()

    db = DBHandler()

    for i in range(0, len(df), batch_size):
        start_time_batch = time.time()

        if i + batch_size > len(df):
            batch = df.iloc[i:]
        else:
            batch = df.iloc[i:i + batch_size]

        total_batches = len(df) // batch_size + 1
        current_batch = i // batch_size + 1

        logger.info(f"Inserting records for rows {i} to {i + len(batch)} (batch {current_batch}/{total_batches})...")
        db.bulk_insert_data(table, batch.to_dict(orient="list"))
        logger.info(f"Batch inserted successfully.")

        elapsed_time_batch = time.time() - start_time_batch
        logger.info(f"Batch execution time: {elapsed_time_batch:.2f} seconds")

    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time for all batches: {elapsed_time:.2f} seconds")
