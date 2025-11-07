
import logging
from datetime import datetime
import json
from base_creator import BaseCreator
import random
from faker import Faker
import uuid


class OrdersCreator(BaseCreator):
    def __init__(self):
        super().__init__('orders_creator')
        self._load_orders_config()

    def _load_orders_config(self):
        self.orders_status = self.service_config['STATUS']
        self.orders_types = self.service_config['TYPE']
        self.complex_config = self.service_config.get('COMPLEX', 'JSON')

    def get_table_name(self):
        return 'orders'

    def create_fake_data(self, type_info):
        type_name = type_info['name']
        provider_name = type_info['provider']
        method = type_info['method']

        self.fake.add_provider(globals()[provider_name])
        fake_value = eval(method, {"fake": self.fake})
        spec = {"type": type_name, "spec": fake_value}
        return spec

    def generate_order_data(self):
        type_info = random.choice(self.orders_types)

        if self.complex_config == 'JSON':
            spec = self.create_fake_data(type_info)
            spec_value = json.dumps(spec)
        else:
            spec_value = None

        random_orders_status = random.choices(
            list(self.orders_status.keys()), weights=list(self.orders_status.values())
        )[0]

        order_data = {
            "order_id": str(uuid.uuid4()),
            "supplier_id": random.randint(1, 150),
            "item_id": random.randint(1, 100),
            "status": random_orders_status,
            "qty": random.randint(1, 20) * 100,
            "net_price": random.randint(1, 500) * 10,
            "tax_rate": random.uniform(1, 10),
            "issued_at": datetime.now(self.local_tz),
            "completed_at": datetime.now(self.local_tz),
            "spec": spec_value,
            "created_at": datetime.now(self.local_tz),
            "updated_at": datetime.now(self.local_tz)
        }

        return order_data

    def insert_data(self):
        engine = self.get_engine()
        orders_table = self.get_table(self.get_table_name(), engine)

        while True:
            self.sleep_random_time()

            order_data = self.generate_order_data()
            insert_stmt = orders_table.insert().values(order_data)

            try:
                with engine.connect() as connection:
                    result = connection.execute(insert_stmt)
                    logging.info(f"Inserted order: {result.inserted_primary_key}")
            except Exception as e:
                logging.error(f"Error inserting order: {e}")


if __name__ == '__main__':
    creator = OrdersCreator()
    creator.run()

