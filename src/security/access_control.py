import logging

logging.basicConfig(level=logging.INFO)

class AccessControl:
    def __init__(self):
        self.clearance_requirements = {
            "basic_operational": 7,
            "counterintelligence": 7,
            "safehouse_locations": 9,
            "general_info": 1
        }

    def has_access(self, agent_level: int, query_type: str) -> bool:
        required_clearance = self.clearance_requirements.get(query_type, 7)
        access_granted = agent_level >= required_clearance
        if not access_granted:
            logging.info(f"Access denied for agent_level {agent_level} on query_type {query_type} (requires {required_clearance})")
        return access_granted

    def required_clearance(self, query_type: str) -> int:
        return self.clearance_requirements.get(query_type, 7)