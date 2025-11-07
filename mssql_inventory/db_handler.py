import logging
import yaml
import os
import sys
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, DatabaseError, SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging


def load_config(config_path="mssql_inventory/config.yml"):
    """
    Load configuration from a YAML file for mssql inventory.
    """
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        logging.info(f"Configuration loaded successfully from {config_path}.")
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}.")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise


class DBConnectionHandler:
    def __init__(self, db_url, timeout_seconds=30, max_retries=3):
        self.db_url = db_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.engine = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type((OperationalError, DatabaseError)),
        reraise=True
    )
    def connect(self, attempt=1):
        try:
            # Let SQLAlchemy parse the URL which may include the driver (eg mssql+pyodbc://...)
            self.engine = create_engine(self.db_url, pool_timeout=self.timeout_seconds)
            logging.info(f"Attempt {attempt}: Database connection established successfully.")
        except (OperationalError, DatabaseError) as e:
            logging.error(f"Attempt {attempt}: Failed to connect to the database: {e}")
            raise
        except SQLAlchemyError as e:
            logging.error(f"Attempt {attempt}: SQLAlchemy error: {e}")
            raise

    def get_engine(self):
        if not self.engine:
            try:
                for attempt in range(1, self.max_retries + 1):
                    try:
                        self.connect(attempt=attempt)
                        break
                    except (OperationalError, DatabaseError) as e:
                        logging.warning(f"Retry {attempt} failed: {e}")
                        if attempt == self.max_retries:
                            logging.error("All retry attempts failed.")
                            raise RetryError(f"All {self.max_retries} retry attempts failed.")
            except RetryError as e:
                logging.error(f"Error: {e}")
                raise
        return self.engine

    def close(self):
        if self.engine:
            try:
                self.engine.dispose()
                logging.info("Database connection closed successfully.")
            except SQLAlchemyError as e:
                logging.error(f"Error closing database connection: {e}")
                raise
