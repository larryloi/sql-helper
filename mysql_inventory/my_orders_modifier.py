import os
import random
import time
import uuid
import yaml
import json
from datetime import datetime, timedelta
import pytz
import sqlalchemy
from sqlalchemy import create_engine, Table, MetaData, select, func, update
from sqlalchemy.sql import text
from multiprocessing import Process
import mysql.connector
from faker import Faker
from faker import Factory as FakerFactory
from faker_vehicle import VehicleProvider
from faker_music import MusicProvider
import logging

logging.basicConfig(
  format="[%(asctime)s] %(levelname)s: %(message)s",
  style="%",
  datefmt="%Y-%m-%d %H:%M:%S",
  level=logging.INFO,
)

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

service_config = config['services']['my_orders_modifier']
db_url = service_config['DATABASE_URL']
wait_time = service_config['WAIT_TIME']
status = service_config['STATUS']
num_processes = service_config['NUM_PROCESSES']
# tmpl_spec = service_config['TMPL_SPEC']
# types = service_config['TYPE']
# retention_hours = service_config['RETENTION_HOURS']

# Randomly define a datetime within the last
rand_last_hours = service_config['RAND_LAST_HOURS']


def modify_data():
    engine = create_engine(db_url)
    metadata = MetaData()
    
    table_name = 'my_orders'
    my_orders = Table(table_name, metadata, autoload_with=engine)


    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        time.sleep(wait_time_seconds)



        with engine.connect() as connection:
            try:
                random_status = random.choices(list(status.keys()), weights=list(status.values()))[0]
                # Randomly define a datetime within the last 3 days
                #random_time = datetime.now(local_tz) - timedelta(days=random.random() * 3)
                
                # Randomly define a datetime within the last 72 hours (3 days * 24 hours)
                random_time = datetime.now(local_tz) - timedelta(hours=random.random() * rand_last_hours)
                
                # Select the first record after the random tim
                select_stmt = select(my_orders).where(my_orders.c.created_at >= random_time).order_by(my_orders.c.id).limit(1)
                result = connection.execute(select_stmt)
                row = result.fetchone()

                if row is not None:
                  # Update the selected record
                  update_stmt = update(my_orders).where(my_orders.c.id == row['id']).values({
                    "status": random_status,
                    "updated_at": datetime.now(local_tz)
                  })

                  logging.info(f"Random time for modifier: {random_time}")
                  logging.info(f"{update_stmt.compile().string} with parameters {update_stmt.compile().params}")
                  
                  connection.execute(update_stmt)
            except sqlalchemy.exc.ProgrammingError:
                pass

if __name__ == "__main__":
    processes = []

    for _ in range(num_processes):
        p = Process(target=modify_data)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

