
# orders_purger.pytz

import os
import sys
import random
import time
import uuid
import yaml
from datetime import datetime, timedelta
import pytz
import sqlalchemy
from sqlalchemy import create_engine, Table, MetaData, update
from sqlalchemy.sql import text, select
from multiprocessing import Process
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging 

local_tz = pytz.timezone('Asia/Macau')


# Load configuration from YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

service_config = config['services']['orders_purger']
wait_time = service_config['WAIT_TIME']
num_processes = service_config['NUM_PROCESSES']
retention_hours = service_config['RETENTION_HOURS']
batch_size = service_config['BATCH_SIZE']

def purge_data():
    engine = create_engine(service_config['DATABASE_URL'])
    metadata = MetaData()
    orders = Table('orders', metadata, autoload_with=engine, schema='inventory.INV')

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        logging.info(f"RETENTION_HOURS: {retention_hours}; Waiting for {wait_time_seconds} seconds before purging...")
        time.sleep(wait_time_seconds)

        with engine.connect() as connection:
            try:
                # Determine the purge range
                
                select_stmt = select([orders.c.order_id]).where(text(f"DATEDIFF(HOUR, updated_at, GETDATE()) > {retention_hours}")).limit(batch_size)
                #logging.info(f"{select_stmt.compile().string} with parameters {select_stmt.compile().params}")
                result = connection.execute(select_stmt)
                rows_to_delete = result.fetchall()

                
                while rows_to_delete:
                    delete_stmt = orders.delete().where(orders.c.order_id.in_([row['order_id'] for row in rows_to_delete]))
                    result = connection.execute(delete_stmt)

                    logging.info(f"{delete_stmt.compile().string} with parameters {delete_stmt.compile().params}")
                    
                    logging.info(f"RETENTION_HOURS: {retention_hours}; Deleted rows: {result.rowcount}")

                    result = connection.execute(select_stmt)
                    rows_to_delete = result.fetchall()

            except sqlalchemy.exc.ProgrammingError:
                continue


if __name__ == "__main__":
    processes = []

    for _ in range(num_processes):
        p = Process(target=purge_data)
        p.start()
        logging.info(f"Process started with PID: {p.pid}")
        processes.append(p)

    for p in processes:
        p.join()

