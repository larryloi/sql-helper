import os
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

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

service_config = config['services']['invoices_modifier']

wait_time = service_config['WAIT_TIME']
class_ = service_config['CLASS']
num_processes = service_config['NUM_PROCESSES']

def modify_data():
    engine = create_engine(service_config['DATABASE_URL'])
    metadata = MetaData()
    invoices = Table('invoices', metadata, autoload_with=engine, schema='inventory.INV')

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        time.sleep(wait_time_seconds)

        with engine.connect() as connection:
            try:
                # Randomly define a datetime within the last 3 days
                random_time = datetime.now(local_tz) - timedelta(days=random.random() * 3)

                # Select the first record after the random time
                select_stmt = select(invoices).where(invoices.c.created_at >= random_time).order_by(invoices.c.id).limit(1)
                result = connection.execute(select_stmt)
                row = result.fetchone()

                if row is not None:
                    # Update the selected record
                    update_stmt = update(invoices).where(invoices.c.id == row['id']).values({
                        "class": random.choice(class_),
                        "updated_at": datetime.now(local_tz)
                    })
                    connection.execute(update_stmt)
            except sqlalchemy.exc.ProgrammingError:
                continue


if __name__ == "__main__":
    processes = []

    for _ in range(num_processes):
        p = Process(target=modify_data)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

