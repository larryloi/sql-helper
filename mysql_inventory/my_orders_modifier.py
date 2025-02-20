### my_orders_modifier.py
import os
import sys
import random
import time
import yaml
from datetime import datetime, timedelta
import pytz
from sqlalchemy import create_engine, Table, MetaData, select, update
from multiprocessing import Process
import logging
from db_handler import DBConnectionHandler, load_config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
config = load_config()

service_config = config['services']['my_orders_modifier']
db_url = service_config['DATABASE_URL']
wait_time = service_config['WAIT_TIME']
status = service_config['STATUS']
num_processes = service_config['NUM_PROCESSES']
rand_last_hours = service_config['RAND_LAST_HOURS']

def modify_data():
    db_handler = DBConnectionHandler(
        db_url=db_url,
        timeout_seconds=config['services']['default_config']['TIMEOUT_SECONDS'],
        max_retries=config['services']['default_config']['MAX_RETRIES']
    )
    metadata = MetaData()

    try:
        db_handler.connect()
        engine = db_handler.get_engine()
        my_orders = Table('my_orders', metadata, autoload_with=engine)

        while True:
            wait_time_seconds = random.randint(wait_time[0], wait_time[1])
            time.sleep(wait_time_seconds)

            with engine.connect() as connection:
                try:
                    random_status = random.choices(list(status.keys()), weights=list(status.values()))[0]
                    random_time = datetime.now(local_tz) - timedelta(hours=random.random() * rand_last_hours)
                    select_stmt = select(my_orders).where(my_orders.c.created_at >= random_time).order_by(my_orders.c.id).limit(1)
                    result = connection.execute(select_stmt)
                    row = result.fetchone()

                    if row is not None:
                        update_stmt = update(my_orders).where(my_orders.c.id == row['id']).values({
                            "status": random_status,
                            "updated_at": datetime.now(local_tz)
                        })

                        logging.info(f"Random time for modifier: {random_time}")
                        logging.info(f"{update_stmt.compile().string} with parameters {update_stmt.compile().params}")

                        connection.execute(update_stmt)
                except sqlalchemy.exc.ProgrammingError:
                    pass
    finally:
        db_handler.close()

if __name__ == "__main__":
    processes = []

    for _ in range(num_processes):
        p = Process(target=modify_data)
        p.start()
        logging.info(f"Process started with PID: {p.pid}")
        processes.append(p)

    for p in processes:
        p.join()
