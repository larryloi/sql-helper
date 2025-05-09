
# orders_creator

import os
import sys
import random
import time
import uuid
import yaml
import json
from datetime import datetime
import pytz
import sqlalchemy
from sqlalchemy import create_engine, Table, MetaData, select, func
from sqlalchemy.sql import text
from multiprocessing import Process

from faker import Faker
from faker import Factory as FakerFactory
from faker_vehicle import VehicleProvider
from faker_music import MusicProvider
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging 

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

service_config = config['services']['orders_creator']

wait_time = service_config['WAIT_TIME']
status = service_config['STATUS']
num_processes = service_config['NUM_PROCESSES']
# tmpl_spec = service_config['TMPL_SPEC']
types = service_config['TYPE']
retention_hours = service_config['RETENTION_HOURS']
complex_config = service_config.get('COMPLEX', 'JSON')  # Get COMPLEX config, default to JSON


def create_fake_data(fake, type_info):
    type_name = type_info['name']
    provider_name = type_info['provider']
    method = type_info['method']

    fake.add_provider(globals()[provider_name])

    fake_value = eval(method)

    #spec = {"type": type_name, "spec": json.dumps(fake_value)}
    spec = {"type": type_name, "spec": fake_value}
    return spec

def insert_data():
    engine = create_engine(service_config['DATABASE_URL'])
    metadata = MetaData()
    orders = Table('orders', metadata, autoload_with=engine, schema='inventory.INV')

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        time.sleep(wait_time_seconds)

        type_info = random.choice(types)
        fake = Faker()

        # Handle COMPLEX configuration
        if complex_config == "JSON":
            spec = create_fake_data(fake, type_info)
            spec_value = json.dumps(spec)
        else:
            spec_value = None  # Set spec to NULL if COMPLEX is NONE    
#        spec = create_fake_data(fake, type_info)
        
#        print (f"{spec}")
#         print(type(spec)) 
#         print(f"----")
#        a = json.dumps(spec)
#        print(type(a))
#        print(f"----{a}")

#        with engine.connect() as connection:
#            total_records = connection.execute(select([func.count()]).select_from(orders)).scalar()
#            print(f"Total records: {total_records}")

        with engine.connect() as connection:
            try:
                random_status = random.choices(list(status.keys()), weights=list(status.values()))[0]

                insert_stmt = orders.insert().values({
                    "order_id": str(uuid.uuid4()),
                    "supplier_id": random.randint(1, 150),
                    "item_id": random.randint(1, 100),
                    "status": random_status,
                    "qty": random.randint(1, 20) * 100,
                    "net_price": random.randint(1, 500) * 10,
                    "issued_at": datetime.now(local_tz),
                    "completed_at": datetime.now(local_tz),
                    "spec": spec_value,
                    "created_at": datetime.now(local_tz),
                    "updated_at": datetime.now(local_tz)
                })

                result = connection.execute(insert_stmt)
                logging.info(f"Inserted: {result.inserted_primary_key}")

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

