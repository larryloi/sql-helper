import uuid
import json
import random
import sqlalchemy
from datetime import datetime
from sqlalchemy import Table, MetaData
from faker_vehicle import VehicleProvider
from faker_music import MusicProvider
import logging

from base_creator import BaseCreator


class OrdersCreator(BaseCreator):
    """
    Orders creator that inherits from BaseCreator.
    Handles orders-specific data generation and insertion.
    """
    
    def __init__(self):
        """Initialize the OrdersCreator."""
        super().__init__('orders_creator')
        self._load_orders_config()
        
    def _load_orders_config(self):
        """Load orders-specific configuration."""
        self.orders_status = self.service_config['STATUS']
        self.orders_types = self.service_config['TYPE']
        self.complex_config = self.service_config.get('COMPLEX', 'JSON')
        
    def get_table_name(self):
        """Return the table name for orders."""
        return 'orders'
        
    def create_fake_data(self, type_info):
        """
        Create fake data based on type information.
        
        Args:
            type_info (dict): Type information containing name, provider, and method
            
        Returns:
            dict: Generated fake data specification
        """
        type_name = type_info['name']
        provider_name = type_info['provider']
        method = type_info['method']
        
        # Add the provider to faker
        self.fake.add_provider(globals()[provider_name])
        
        # Generate fake value using eval (note: eval should be used carefully in production)
        # Make fake available in the eval context
        fake_value = eval(method, {"fake": self.fake})
        
        spec = {"type": type_name, "spec": fake_value}
        return spec
        
    def generate_order_data(self):
        """
        Generate data for a single order.
        
        Returns:
            dict: Dictionary containing order data
        """
        type_info = random.choice(self.orders_types)
        
        # Handle COMPLEX configuration
        if self.complex_config == "JSON":
            spec = self.create_fake_data(type_info)
            spec_value = json.dumps(spec)
        else:
            spec_value = None  # Set spec to NULL if COMPLEX is NONE
            
        # Generate random order status based on weights
        random_orders_status = random.choices(
            list(self.orders_status.keys()), 
            weights=list(self.orders_status.values())
        )[0]
        
        # Generate order data
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
        """
        Main data insertion loop for orders.
        This method runs continuously and inserts order data.
        """
        engine = self.get_engine()
        metadata = MetaData()
        table_name = self.get_table_name()
        orders_table = Table(table_name, metadata, autoload_with=engine)
        
        while True:
            # Sleep for random time
            self.sleep_random_time()
            
            # Generate order data
            order_data = self.generate_order_data()
            
            # Create insert statement
            insert_stmt = orders_table.insert().values(order_data)
            
            try:
                with engine.connect() as connection:
                    result = connection.execute(insert_stmt)
                    logging.info(f"Inserted order: {result.inserted_primary_key}")
                    
            except sqlalchemy.exc.ProgrammingError as e:
                logging.error(f"Database error: {e}")
                
            except Exception as e:
                logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    """Main entry point for the orders creator."""
    creator = OrdersCreator()
    creator.run()