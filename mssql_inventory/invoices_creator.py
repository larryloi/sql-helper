import os
import sys
import random
import time
import uuid
import os
import random
import time
import uuid
import logging
from datetime import datetime
import pytz
from multiprocessing import Process

from db_handler import load_config, DBConnectionHandler

local_tz = pytz.timezone('Asia/Macau')

# Load configuration
config = load_config()
default_config = config['services']['default_config']
service_config = config['services'].get('invoices_creator', {})

wait_time = service_config.get('WAIT_TIME', [1, 3])
class_ = service_config.get('CLASS', [])
num_processes = service_config.get('NUM_PROCESSES', 1)
retention_hours = service_config.get('RETENTION_HOURS', 24)

def insert_data():
    db_url = service_config.get('DATABASE_URL') or default_config.get('DATABASE_URL')
    handler = DBConnectionHandler(db_url, timeout_seconds=default_config.get('TIMEOUT_SECONDS', 30), max_retries=default_config.get('MAX_RETRIES', 3))
    engine = handler.get_engine()
    metadata = __import__('sqlalchemy').MetaData()
    schema = service_config.get('SCHEMA') or default_config.get('SCHEMA')
    invoices = __import__('sqlalchemy').Table('invoices', metadata, autoload_with=engine, schema=schema)

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        time.sleep(wait_time_seconds)

        with engine.connect() as connection:
            try:
                insert_stmt = invoices.insert().values({
                    "invoice_id": str(uuid.uuid4()),
                    "customer_id": random.randint(1, 30),
                    "item_id": random.randint(1, 100),
                    "class": random.choice(class_) if class_ else None,
                    "qty": random.randint(1, 20) * 100,
                    "price": random.randint(1, 500) * 10,
                    "created_at": datetime.now(local_tz),
                    "updated_at": datetime.now(local_tz)
                })
                connection.execute(insert_stmt)

                delete_stmt = invoices.delete().where(__import__('sqlalchemy').text(f"DATEDIFF(hour, updated_at, GETDATE()) > {retention_hours}"))
                connection.execute(delete_stmt)
            except Exception:
                continue


if __name__ == "__main__":
    processes = []

    for _ in range(num_processes):
        p = Process(target=insert_data)
        p.start()
        logging.info(f"Process started with PID: {p.pid}")
        processes.append(p)

    for p in processes:
        p.join()
        p.join()


