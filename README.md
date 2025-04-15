# Agent WebSocket Application

An agent application with FastAPI and WebSocket support, designed for running AI agents.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Create a `.env` file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   MODEL_ID=claude-3-7-sonnet-latest
   AUTHORIZED_IMPORTS=math,random,datetime,json,re
   ```

4. Run the development server:
   ```bash
   python -m src.agent.server
   ```

## Project Structure

```
.
├── src/
│   ├── agent/              # Agent package
│   │   ├── __init__.py     # Package initialization
│   │   ├── agent.py        # Main agent implementation
│   │   ├── code_executor.py # Code execution module
│   │   ├── llm.py          # LLM interaction module
│   │   ├── prompts.py      # System prompts
│   │   ├── server.py       # WebSocket server
│   │   ├── state_manager.py # Agent state management
│   │   └── tools.py        # Agent tools implementation
│   └── tests/            # Test modules
├── static/               # Static files for the web UI
├── pyproject.toml        # Project configuration
├── gunicorn_conf.py      # Gunicorn configuration
└── README.md
```

## WebSocket Usage

Connect to the WebSocket endpoint at:
```
ws://localhost:8000/ws/{client_id}
```

## Production Deployment

Run with Gunicorn:
```bash
gunicorn src.agent.server:app -c gunicorn_conf.py
```
