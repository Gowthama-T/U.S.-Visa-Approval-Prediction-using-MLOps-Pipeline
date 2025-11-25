import logging
import os
from datetime import datetime
from from_root import from_root

# Log file name
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Logs directory in project root
log_dir = os.path.join(from_root(), "logs")
os.makedirs(log_dir, exist_ok=True)

# Full log file path
logs_path = os.path.join(log_dir, LOG_FILE)

# Configure logging
logging.basicConfig(
    filename=logs_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)
