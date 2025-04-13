from typing import Tuple
from groq import Groq
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class LLMArbitrator:
    def __init__(self, model: str = "llama3-70b-8192"):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in .env file or environment variables")
        try:
            self.client = Groq(api_key=groq_api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Groq client: {str(e)}")
            raise
        self.model = model
        self.query_types = [
            "basic_operational", "advanced_covert", "tech_encryption", "counterintelligence",
            "cyber_intel", "psych_warfare", "high_level_ops", "misc_security", "universal"
        ]

    def classify(self, query: str) -> Tuple[str, float]:
        prompt = (
        "Classify the following query into one of the predefined categories based on its theme. "
        "Return ONLY the category key (e.g., 'basic_operational', 'cyber_intel', etc.) from the list below:\n\n"
        "Categories:\n"
        "- basic_operational: Training, protocols, extraction, evasion\n"
        "- advanced_covert: Safehouses, dead-drops, disguises\n"
        "- tech_encryption: Encryption, decryption, neural systems\n"
        "- counterintelligence: Double agents, financial tracking\n"
        "- cyber_intel: Drones, digital forensics, masking\n"
        "- psych_warfare: Psychological tactics, misinformation\n"
        "- high_level_ops: Strategic operations, military tactics\n"
        "- misc_security: Evasion, profiling, security\n"
        "- universal: General or ambiguous queries\n\n"
        f"Query: {query}\n\n"
        "Respond with only the category key (e.g., 'cyber_intel')."
    )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            query_type = response.choices[0].message.content.strip()
            if query_type not in self.query_types:
                query_type = "universal"

            return query_type
        except Exception as e:
            logging.error(f"Groq API error: {str(e)}")
            return "universal"