from typing import Optional, Dict, List, Set
import json
import logging
import re
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO)

class RuleEngine:
    def __init__(self, rules_path: str = "rules/rules.json"):
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                self.rules = json.load(f)
            total_rules = sum(len(v) for v in self.rules.values())
            logging.info(f"Loaded {total_rules} rules from {rules_path}")
        except Exception as e:
            logging.error(f"Failed to load rules: {str(e)}")
            self.rules = {}
        
        self.greetings = {
            1: "Salute, Shadow Cadet.",
            2: "Bonjour, Sentinel.",
            3: "Eyes open, Phantom.",
            4: "In the wind, Commander.",
            5: "The unseen hand moves, Whisper.",
            7: "Eyes open, Phantom.",
            9: "The unseen hand moves, Whisper."
        }
        self.stop_words = {'is', 'the', 'what', 'for', 'in', 'a', 'to', 'about', 'how', 'on', 'and', 'of', 'at', 'by', 'with', 'does'}
        self.condition_keywords = self.precompute_condition_keywords()

    def precompute_condition_keywords(self) -> Dict[int, Set[str]]:
        condition_keywords = {}
        index = 0
        for category, rules in self.rules.items():
            for rule in rules:
                condition = rule["condition"].lower().replace("if ", "").strip()
                words = re.findall(r'\b\w+\b', condition)
                keywords = {word for word in words if word not in self.stop_words}
                condition_keywords[index] = keywords
                index += 1
        return condition_keywords

    def apply(self, query: str, query_type: str, agent_level: int) -> Optional[str]:
        try:
            query_lower = query.lower().strip()
            applicable_rules = self.rules.get(query_type, []) + self.rules.get("universal", [])
            if not applicable_rules:
                applicable_rules = []
                for cat, rules in self.rules.items():
                    applicable_rules.extend(rules)
            logging.debug(f"Applicable rules count: {len(applicable_rules)} for query: {query}, type: {query_type}, level: {agent_level}")

            query_words = re.findall(r'\b\w+\b', query_lower)
            query_keywords = {word for word in query_words if word not in self.stop_words}

            for i, rule in enumerate(applicable_rules):
                condition = rule["condition"].lower()
                response = rule.get("response", "")
                required_level = rule.get("agent_level", None)

                if "after 2 am utc" in condition and "facility x-17" in query_lower:
                    if datetime.now(pytz.UTC).hour >= 2:
                        greeting = self.greetings.get(agent_level, "Greetings, Agent.")
                        logging.info(f"Applied rule: {condition} for level {agent_level}")
                        return f"{greeting} {response}"
                    continue

                condition_keys = self.condition_keywords.get(i, set())
                if not condition_keys:
                    continue

                matched_keys = condition_keys & query_keywords
                match_ratio = len(matched_keys) / len(condition_keys) if condition_keys else 0

                threshold = 1.0 if len(condition_keys) <= 2 else 0.75
                if match_ratio >= threshold:
                    if required_level is None or agent_level == required_level:
                        greeting = self.greetings.get(agent_level, "Greetings, Agent.")
                        logging.info(f"Applied rule: {condition} for level {agent_level}, match ratio: {match_ratio:.2f}")
                        return f"{greeting} {response}"

            logging.info(f"No rule matched for query: {query}, type: {query_type}")
            return None
        except Exception as e:
            logging.error(f"Rule engine failed: {str(e)}")
            return None