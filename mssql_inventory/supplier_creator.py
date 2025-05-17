import os
import sys
import random
import time
import yaml
from datetime import datetime
from faker import Faker
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, text, select, func 
from multiprocessing import Process
import pytz
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging

local_tz = pytz.timezone('Asia/Macau')

# Load configuration from YAML file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

service_config = config['services']['supplier_creator']

wait_time = service_config['WAIT_TIME']
supplier_types = service_config['TYPE']
num_processes = service_config['NUM_PROCESSES']

def generate_unique_supplier_name(connection, fake):
    """Generate a unique supplier name using database check"""
    while True:
        supplier_name = fake.company() + ' ' + fake.company_suffix()
        query = text("SELECT COUNT(*) FROM inventory.INV.suppliers WHERE name = :name")
        result = connection.execute(query, {'name': supplier_name}).scalar()
        if result == 0:
            return supplier_name

def insert_supplier_data():
    """Main worker function for inserting supplier data"""
    fake = Faker()  # Each process gets its own Faker instance
    engine = create_engine(service_config['DATABASE_URL'])
    metadata = MetaData()
    
    # Reflect existing table structure
    suppliers_table = Table('suppliers', metadata, autoload_with=engine, schema='inventory.INV')

    while True:
        try:
            # Random wait between operations
            wait_time_seconds = random.randint(wait_time[0], wait_time[1])
            time.sleep(wait_time_seconds)

            with engine.connect() as connection:
                # Generate unique supplier name
                supplier_name = generate_unique_supplier_name(connection, fake)
                supplier_type = random.choice(supplier_types)
                current_time = datetime.now(local_tz)

                # Prepare and execute insert statement
                insert_stmt = suppliers_table.insert().values(
                    name=supplier_name,
                    type=supplier_type,
                    created_at=current_time,
                    updated_at=current_time
                )

                result = connection.execute(insert_stmt)
                #connection.commit()
                logging.info(f"Successfully inserted supplier ID: {result.inserted_primary_key}")

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            time.sleep(1)  # Prevent tight error loop

if __name__ == "__main__":
    processes = []

    # Start worker processes
    for _ in range(num_processes):
        p = Process(target=insert_supplier_data)
        p.start()
        logging.info(f"Started process with PID: {p.pid}")
        processes.append(p)

    # Wait for all processes to complete
    for p in processes:
        p.join()