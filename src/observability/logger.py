import logging
import json
import csv
import os
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class LogEntry:
    timestamp: str
    service_name: str
    error_category: str
    retry_count: int
    circuit_breaker_state: str
    message: str

class StructuredLogger:
    def __init__(self, log_file="system_logs.json"):
        self.log_file = log_file
        # Ensure log file exists or clean it
        with open(self.log_file, 'w') as f:
            f.write("")
            
        self.logger = logging.getLogger("StructuredLogger")
        self.logger.setLevel(logging.INFO)
        
        # Console handler for debugging
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def log(self, entry: LogEntry):
        """Logs an entry to the JSON file."""
        data = asdict(entry)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(data) + "\n")
        
        # Also log to standard python logging for console visibility
        self.logger.info(f"Logged: {data}")

class GoogleSheetsLogger:
    def __init__(self, sheet_file="mock_google_sheets.csv"):
        self.sheet_file = sheet_file
        # Initialize CSV with headers if not exists
        if not os.path.exists(self.sheet_file):
            with open(self.sheet_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Service", "Category", "Retries", "CB State", "Message"])

    def log(self, entry: LogEntry):
        """Simulates logging to a Google Sheet by appending to a CSV."""
        with open(self.sheet_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry.timestamp,
                entry.service_name,
                entry.error_category,
                entry.retry_count,
                entry.circuit_breaker_state,
                entry.message
            ])
        print(f"[Google Sheets Mock] Appended row: {entry.service_name} - {entry.message}")

# Singleton instance for global access if needed, 
# although dependency injection is cleaner.
# We will instantiate these in main.
