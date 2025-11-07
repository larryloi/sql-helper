import logging
import random
from datetime import datetime
from base_creator import BaseCreator
from faker import Faker


class SupplierCreator(BaseCreator):
    def __init__(self):
        super().__init__('supplier_creator')
        self._load_supplier_config()

    def _load_supplier_config(self):
        self.supplier_types = self.service_config['TYPE']

    def get_table_name(self):
        return 'suppliers'

    def generate_unique_supplier_name(self, connection):
        metadata = __import__('sqlalchemy').MetaData()
        suppliers_table = self.get_table(self.get_table_name(), connection.engine if hasattr(connection, 'engine') else self.get_engine())

        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            supplier_name = self.fake.company() + ' ' + self.fake.company_suffix()
            try:
                select_stmt = suppliers_table.select().where(suppliers_table.c.name == supplier_name)
                result = connection.execute(select_stmt)
                # If zero rows, return
                row = result.fetchone()
                if not row:
                    return supplier_name
            except Exception:
                logging.warning("Error checking supplier name uniqueness")
            attempts += 1

        import uuid
        return f"{self.fake.company()} {self.fake.company_suffix()} {str(uuid.uuid4())[:8]}"

    def generate_supplier_data(self, connection):
        supplier_name = self.generate_unique_supplier_name(connection)
        supplier_type = random.choice(self.supplier_types)

        supplier_data = {
            "name": supplier_name,
            "type": supplier_type,
            "created_at": datetime.now(self.local_tz),
            "updated_at": datetime.now(self.local_tz)
        }

        return supplier_data

    def insert_data(self):
        engine = self.get_engine()
        suppliers_table = self.get_table(self.get_table_name(), engine)

        while True:
            self.sleep_random_time()
            try:
                with engine.connect() as connection:
                    supplier_data = self.generate_supplier_data(connection)
                    insert_stmt = suppliers_table.insert().values(supplier_data)
                    result = connection.execute(insert_stmt)
                    logging.info(f"Inserted supplier: {supplier_data['name']} (ID: {result.inserted_primary_key})")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                continue


if __name__ == '__main__':
    creator = SupplierCreator()
    creator.run()