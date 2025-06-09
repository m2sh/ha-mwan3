"""Constants for the MWAN3 integration."""
from datetime import timedelta

DOMAIN = "mwan3"

CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30  # seconds
MIN_SCAN_INTERVAL = 10  # Minimum 10 seconds between updates
MAX_SCAN_INTERVAL = 3600  # 1 hour 