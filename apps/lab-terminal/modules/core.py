import os
import yaml
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

import re

# Ensure directory for forged skills
FORGED_SKILLS_DIR = os.path.join(os.path.dirname(__file__), '../forged_skills')
os.makedirs(FORGED_SKILLS_DIR, exist_ok=True)

def slugify(text):
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')

PERSONAS = {}
DEFAULT_PERSONA = "coda"

def load_personas():
    global PERSONAS
    try:
        # Adjusted path to go up from modules/ to apps/lab-terminal/ then to apps/riko_project/
        config_path = os.path.join(os.path.dirname(__file__), '../../riko_project/character_config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            PERSONAS = config.get('presets', {})
        print(f"Loaded {len(PERSONAS)} personas.")
    except Exception as e:
        print(f"Warning: Could not load character config: {e}")
        PERSONAS = {
            "coda": {
                "name": "Coda",
                "description": "System Core",
                "system_prompt": "You are the Coda Interface system core."
            }
        }

load_personas()
