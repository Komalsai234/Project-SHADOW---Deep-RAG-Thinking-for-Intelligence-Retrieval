import logging
from datetime import datetime
import json
import hashlib
from typing import Dict

logging.basicConfig(level=logging.INFO)

class AuditLedger:
    def __init__(self, log_path: str = "audit_ledger/audit.jsonl"):
        self.log_path = log_path
        self.previous_hash = None

    def log(self, event: Dict):
        event["timestamp"] = datetime.utcnow().isoformat()
        if self.previous_hash:
            event["previous_hash"] = self.previous_hash
        event_str = json.dumps(event, sort_keys=True)
        event_hash = hashlib.sha256(event_str.encode()).hexdigest()
        event["event_hash"] = event_hash
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")
        self.previous_hash = event_hash
        logging.info(f"Audit logged: {event['action']}")