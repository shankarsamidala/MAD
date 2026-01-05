"""
Configuration for MAD (Multi-Agent Debate) System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Model Configuration per Agent
# Using OpenAI + Groq + Ollama (Gemini quota exhausted)
AGENT_MODELS = {
    "advocate": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.7
    },
    "critic": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.6
    },
    "contrarian": {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",  # Smaller, faster model for diversity
        "temperature": 0.8
    },
    "domain_expert": {
        "provider": "ollama",
        "model": OLLAMA_MODEL,
        "temperature": 0.5
    },
    "synthesizer": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.6
    },
    "judge": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.4
    }
}

# Debate Configuration
DEBATE_CONFIG = {
    "max_rounds": 2,  # Number of adversarial rounds
    "enable_domain_expert": False,  # Disabled - Ollama EC2 port not open
    "verbose": True
}
