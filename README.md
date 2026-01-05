# MAD System - Multi-Agent Debate Framework

A multi-agent debate system that uses 6 AI agents with different perspectives to analyze strategic decisions, breaking the "AI Hivemind" problem.

## Quick Start

### 1. Install Dependencies

```bash
cd mad-system
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example env file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
- `OPENAI_API_KEY` - From OpenAI
- `GOOGLE_API_KEY` - From Google AI Studio
- `GROQ_API_KEY` - From Groq Console
- Ollama should be running locally on port 11434

### 3. Run the App

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## How It Works

You enter a strategic question, and 6 AI agents debate it:

| Agent | Role | Model |
|-------|------|-------|
| Advocate | Builds case FOR the proposal | OpenAI GPT-4o |
| Critic | Identifies risks & weaknesses | Groq Llama 3.1 70B |
| Contrarian | Proposes alternatives | Google Gemini |
| Domain Expert | Reality check | Ollama (local) |
| Synthesizer | Integrates all viewpoints | OpenAI GPT-4o |
| Judge | Final assessment | Groq Llama 3.1 70B |

## Debate Flow

```
Round 1: Initial Positions (Advocate, Critic, Contrarian - parallel)
    ↓
Round 2: Adversarial Exchange (Advocate responds to Critic)
    ↓
Round 3: Domain Expert Reality Check
    ↓
Synthesis: Options synthesized from debate
    ↓
Judgment: Final assessment and recommendation
```

## Configuration

Edit `config.py` to:
- Change which model each agent uses
- Adjust temperature settings
- Enable/disable domain expert
- Configure debate rounds

## Project Structure

```
mad-system/
├── agents/           # Agent definitions with prompts
│   ├── advocate.py
│   ├── critic.py
│   ├── contrarian.py
│   ├── domain_expert.py
│   ├── synthesizer.py
│   └── judge.py
├── workflows/        # Debate orchestration
│   └── debate_flow.py
├── utils/            # LLM factory
│   └── llm_factory.py
├── app.py            # Streamlit UI
├── config.py         # Configuration
└── requirements.txt
```

## Requirements

- Python 3.10+
- API keys for OpenAI, Google Gemini, Groq
- Ollama running locally (optional, for Domain Expert)
