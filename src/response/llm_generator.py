from groq import Groq
from typing import List, Dict
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class LLMGenerator:
    def __init__(self, model: str = "llama3-70b-8192"):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in .env file or environment variables")
        
        logging.info(f"Initializing Groq client with model: {model}")
        logging.info(f"Environment proxies: HTTP_PROXY={os.getenv('HTTP_PROXY')}, HTTPS_PROXY={os.getenv('HTTPS_PROXY')}")
        
        try:
            self.client = Groq(api_key=groq_api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Groq client: {str(e)}")
            raise
        self.model = model
        self.greetings = {
            1: "Salute, Shadow Cadet.",
            2: "Greetings, Operative.",
            3: "Well met, Agent.",
            4: "Eyes sharp, Specialist.",
            5: "Stay vigilant, Enigma.",
            7: "Eyes open, Phantom.",
            9: "The unseen hand moves, Whisper."
        }

    def generate(self, query: str, results: List[Dict], agent_level: int, denied_due_to_clearance: bool = False) -> str:
        greeting = self.greetings.get(agent_level, "Greetings, Agent.")

        if denied_due_to_clearance:
            return f"{greeting} Access Denied."
        

        if not results:
            return f"{greeting} No relevant information found for your query."

        try:
            context = "\n".join([
                f"{i+1}. {r['content']} (Source: {r.get('source', r['metadata'].get('doc_id', 'Secret Info Manual'))})"
                for i, r in enumerate(results)
            ])
            prompt = (
                f"Query: {query}\n\n"
                f"Context:\n{context}\n\n"
                f"Provide a concise, accurate response based on the context, including a justification for the answer. "
                f"Ensure the response respects the agent's clearance level ({agent_level})."
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"LLM generation failed: {str(e)}")
            return f"{greeting} Error generating response: {str(e)}"