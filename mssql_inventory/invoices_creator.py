import os
import sys
import random
import time
import uuid
import yaml
from datetime import datetime
import pytz
import sqlalchemy
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import text
from multiprocessing import Process
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging 

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

service_config = config['services']['invoices_creator']

wait_time = service_config['WAIT_TIME']
class_ = service_config['CLASS']
num_processes = service_config['NUM_PROCESSES']
retention_hours = service_config['RETENTION_HOURS']

def insert_data():
    engine = create_engine(service_config['DATABASE_URL'])
    metadata = MetaData()
    invoices = Table('invoices', metadata, autoload_with=engine, schema='inventory.INV')

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        time.sleep(wait_time_seconds)

        with engine.connect() as connection:
            try:
                # Insert new invoice
                insert_stmt = invoices.insert().values({
                    "invoice_id": str(uuid.uuid4()),
                    "customer_id": random.randint(1, 30),
                    "item_id": random.randint(1, 100),
                    "class": random.choice(class_),
                    "qty": random.randint(1, 20) * 100,
                    "price": random.randint(1, 500) * 10,
                    "created_at": datetime.now(local_tz),
                    "updated_at": datetime.now(local_tz)
                })
                connection.execute(insert_stmt)


                delete_stmt = invoices.delete().where(text(f"DATEDIFF(hour, updated_at, GETDATE()) > {retention_hours}"))
                connection.execute(delete_stmt)
                #print (f"{delete_stmt}")
            except sqlalchemy.exc.ProgrammingError:
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

