# db_handler.py
import logging
import yaml
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, DatabaseError

# Function to load configuration from config.yml
def load_config(config_path="config.yml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config

class DBConnectionHandler:
    def __init__(self, db_url, timeout_seconds=30, max_retries=3):
        self.db_url = db_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.engine = None

    @retry(
        stop=stop_after_attempt(3),  # Maximum number of retries
        wait=wait_fixed(2),  # Wait 2 seconds between retries
        retry=retry_if_exception_type((OperationalError, DatabaseError)),  # Retry on these exceptions
        reraise=True
    )
    def connect(self, attempt=1):
        """Establish a database connection with retry logic."""
        try:
            self.engine = create_engine(self.db_url, pool_timeout=self.timeout_seconds)
            logging.info(f"Attempt {attempt}: Database connection established successfully.")
        except (OperationalError, DatabaseError) as e:
            logging.error(f"Attempt {attempt}: Failed to connect to the database: {e}")
            raise

    def get_engine(self):
        """Return the SQLAlchemy engine."""
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
        """Close the database connection."""
        if self.engine:
            self.engine.dispose