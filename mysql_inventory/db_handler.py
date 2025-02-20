import logging
import yaml
import os
import sys
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, DatabaseError, SQLAlchemyError

# Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
import my_logging

def load_config(config_path="mysql_inventory/config.yml"):
    """
    Load configuration from a YAML file.
    
    Args:
        config_path (str): Path to the configuration file.
    
    Returns:
        dict: Loaded configuration.
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
        """
        Initialize the database connection handler.
        
        Args:
            db_url (str): Database connection URL.
            timeout_seconds (int): Connection timeout in seconds.
            max_retries (int): Maximum number of retry attempts.
        """
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
        """
        Establish a database connection with retry logic.
        
        Args:
            attempt (int): Current retry attempt number.
        """
        try:
            self.engine = create_engine(self.db_url, pool_timeout=self.timeout_seconds)
            logging.info(f"Attempt {attempt}: Database connection established successfully.")
        except (OperationalError, DatabaseError) as e:
            logging.error(f"Attempt {attempt}: Failed to connect to the database: {e}")
            raise
        except SQLAlchemyError as e:
            logging.error(f"Attempt {attempt}: SQLAlchemy error: {e}")
            raise

    def get_engine(self):
        """
        Return the SQLAlchemy engine.
        
        Returns:
            sqlalchemy.engine.Engine: The database engine.
        
        Raises:
            RetryError: If all retry attempts fail.
        """
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
        """
        Close the database connection and dispose of the engine.
        """
        if self.engine:
            try:
                self.engine.dispose()
                logging.info("Database connection closed successfully.")
            except SQLAlchemyError as e:
                logging.error(f"Error closing database connection: {e}")
                raise