"""
LLM Factory - Creates LLM instances for CrewAI v1.x
Uses CrewAI's native LLM class with LiteLLM model strings
Supports: OpenAI, Google Gemini, Groq, Ollama
"""
from crewai import LLM
import config


def get_llm(agent_name: str) -> LLM:
    """
    Get the appropriate LLM instance for an agent based on configuration.

    CrewAI v1.x uses LiteLLM format for model strings:
    - OpenAI: "openai/gpt-4o" or just "gpt-4o"
    - Gemini: "gemini/gemini-1.5-flash"
    - Groq: "groq/llama-3.1-70b-versatile"
    - Ollama: "ollama/llama3.1"

    Args:
        agent_name: Name of the agent (advocate, critic, contrarian, domain_expert, synthesizer, judge)

    Returns:
        CrewAI LLM instance configured for the agent
    """
    agent_config = config.AGENT_MODELS.get(agent_name)

    if not agent_config:
        raise ValueError(f"Unknown agent: {agent_name}")

    provider = agent_config["provider"]
    model = agent_config["model"]
    temperature = agent_config.get("temperature", 0.7)

    # Build LiteLLM model string based on provider
    if provider == "openai":
        model_string = f"openai/{model}"
        return LLM(
            model=model_string,
            temperature=temperature,
            api_key=config.OPENAI_API_KEY
        )

    elif provider == "google":
        model_string = f"gemini/{model}"
        return LLM(
            model=model_string,
            temperature=temperature,
            api_key=config.GOOGLE_API_KEY
        )

    elif provider == "groq":
        model_string = f"groq/{model}"
        return LLM(
            model=model_string,
            temperature=temperature,
            api_key=config.GROQ_API_KEY
        )

    elif provider == "ollama":
        model_string = f"ollama/{model}"
        return LLM(
            model=model_string,
            temperature=temperature,
            base_url=config.OLLAMA_BASE_URL
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")


def test_all_connections():
    """Test connections to all configured LLM providers."""
    results = {}

    for agent_name in config.AGENT_MODELS.keys():
        try:
            llm = get_llm(agent_name)
            # CrewAI LLM uses .call() method
            response = llm.call("Say 'OK' if you're working.")
            results[agent_name] = {
                "status": "success",
                "provider": config.AGENT_MODELS[agent_name]["provider"],
                "model": config.AGENT_MODELS[agent_name]["model"]
            }
        except Exception as e:
            results[agent_name] = {
                "status": "error",
                "provider": config.AGENT_MODELS[agent_name]["provider"],
                "error": str(e)
            }

    return results
