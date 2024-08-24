import os
import yaml
import random
import time
from datetime import datetime, timedelta
import pytz
import sqlalchemy
from sqlalchemy import create_engine, Table, MetaData, select, func
from sqlalchemy.sql import text
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

service_config = config['services']['my_orders_purger']
db_url = service_config['DATABASE_URL']
wait_time = service_config['WAIT_TIME']
retention_hours = service_config['RETENTION_HOURS']
batch_size = service_config['BATCH_SIZE']

def purge_data():
    engine = create_engine(db_url)
    metadata = MetaData()
    table_name = 'my_orders'
    my_orders = Table(table_name, metadata, autoload_with=engine)

    while True:
        wait_time_seconds = random.randint(wait_time[0], wait_time[1])
        logging.info(f"Waiting for {wait_time_seconds} seconds before purging...")
        time.sleep(wait_time_seconds)

        with engine.connect() as connection:
            try:
                # Determine the purge range
                select_stmt = select([my_orders.c.order_id]).where(text(f"TIMESTAMPDIFF(HOUR, updated_at, NOW()) > {retention_hours}")).limit(batch_size)
                logging.info(f"{select_stmt.compile().string} with parameters {select_stmt.compile().params}")
                result = connection.execute(select_stmt)
                rows_to_delete = result.fetchall()


                while rows_to_delete:
                    delete_stmt = my_orders.delete().where(my_orders.c.order_id.in_([row['order_id'] for row in rows_to_delete]))
                    result = connection.execute(delete_stmt)
                    #print(delete_stmt)
                    #current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    #print(f"[{current_time}] INFO: {delete_stmt.compile().string} with parameters {delete_stmt.compile().params}")
                    logging.info(f"{delete_stmt.compile().string} with parameters {delete_stmt.compile().params}")
                    #print(f"[{current_time}] INFO: Deleted rows: {result.rowcount}")
                    logging.info(f"Deleted rows: {result.rowcount}")

                    result = connection.execute(select_stmt)
                    rows_to_delete = result.fetchall()

            except sqlalchemy.exc.ProgrammingError:
                continue

if __name__ == "__main__":
    purge_data()
