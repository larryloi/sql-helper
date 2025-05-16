### orders_purger.py
import os
import sys
import yaml
import random
import time
from datetime import datetime, timedelta
import pytz
import sqlalchemy
from sqlalchemy import create_engine, Table, MetaData, select, func
from sqlalchemy.sql import text
import logging
from db_handler import DBConnectionHandler, load_config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging 

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
config = load_config()

service_config = config['services']['orders_purger']
db_url = service_config['DATABASE_URL']
wait_time = service_config['WAIT_TIME']
retention_hours = service_config['RETENTION_HOURS']
batch_size = service_config['BATCH_SIZE']

def purge_data():
    logging.info(f"Process started with PID: {os.getpid()}")
    engine = create_engine(db_url)
    metadata = MetaData()
    table_name = 'orders'
    orders = Table(table_name, metadata, autoload_with=engine)

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        logging.info(f"RETENTION_HOURS: {retention_hours}; Waiting for {wait_time_seconds} seconds before purging...")
        time.sleep(wait_time_seconds)

        with engine.connect() as connection:
            try:
                # Determine the purge range
                select_stmt = select([orders.c.order_id]).where(text(f"TIMESTAMPDIFF(HOUR, updated_at, NOW()) > {retention_hours}")).limit(batch_size)
                #logging.info(f"{select_stmt.compile().string} with parameters {select_stmt.compile().params}")
                result = connection.execute(select_stmt)
                rows_to_delete = result.fetchall()


                while rows_to_delete:
                    delete_stmt = orders.delete().where(orders.c.order_id.in_([row['order_id'] for row in rows_to_delete]))
                    result = connection.execute(delete_stmt)
                    #print(delete_stmt)
                    #current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    #print(f"[{current_time}] INFO: {delete_stmt.compile().string} with parameters {delete_stmt.compile().params}")
                    logging.info(f"{delete_stmt.compile().string} with parameters {delete_stmt.compile().params}")
                    #print(f"[{current_time}] INFO: Deleted rows: {result.rowcount}")
                    logging.info(f"RETENTION_HOURS: {retention_hours}; Deleted rows: {result.rowcount}")

                    result = connection.execute(select_stmt)
                    rows_to_delete = result.fetchall()

            except sqlalchemy.exc.ProgrammingError:
                continue

if __name__ == "__main__":
    purge_data()
