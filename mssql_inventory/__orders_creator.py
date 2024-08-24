import os
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

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

service_config = config['services']['orders_creator']

wait_time = service_config['WAIT_TIME']
status = service_config['STATUS']
num_processes = service_config['NUM_PROCESSES']
retention_hours = service_config['RETENTION_HOURS']


def insert_data():
    engine = create_engine(service_config['DATABASE_URL'])
    metadata = MetaData()
    orders = Table('orders', metadata, autoload_with=engine, schema='inventory.INV')

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        time.sleep(wait_time_seconds)


        with engine.connect() as connection:
            try:
                random_status = random.choices(list(status.keys()), weights=list(status.values()))[0]

                insert_stmt = orders.insert().values({
                    "order_id": str(uuid.uuid4()),
                    "supplier_id": random.randint(1, 30),
                    "item_id": random.randint(1, 100),
                    "status": random_status,
                    "qty": random.randint(1, 20) * 100,
                    "net_price": random.randint(1, 500) * 10,
                    "issued_at": datetime.now(local_tz),
                    "created_at": datetime.now(local_tz),
                    "updated_at": datetime.now(local_tz)
                })
                connection.execute(insert_stmt)
                
                # print (f"Retention hours: {retention_hours}....")
                delete_stmt = orders.delete().where(text(f"DATEDIFF(hour, updated_at, GETDATE()) > {retention_hours}"))
                # print (f"Executing... Statment")
                # print (f"{delete_stmt}")
                connection.execute(delete_stmt)
            except sqlalchemy.exc.ProgrammingError:
                continue

if __name__ == "__main__":
    processes = []

    for _ in range(num_processes):
        p = Process(target=insert_data)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

