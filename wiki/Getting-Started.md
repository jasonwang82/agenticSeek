# Getting Started

This guide will help you install, configure, and run AgenticSeek.

## Prerequisites

- **Python 3.10+**
- **Git**
- **Ollama** (for local LLMs) or API keys for cloud providers
- **Docker** (optional, for web UI and search services)
- **GPU** (recommended for local LLMs, see [Hardware Requirements](Home#hardware-requirements))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/agenticSeek.git
cd agenticSeek
```

### 2. Set Up Python Environment

```bash
python3 -m venv agentic_seek_env
source agentic_seek_env/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys (if using cloud providers):

```bash
SEARXNG_BASE_URL="http://127.0.0.1:8080"
OPENAI_API_KEY='your-openai-key'
DEEPSEEK_API_KEY='your-deepseek-key'
OPENROUTER_API_KEY='your-openrouter-key'
```

### 4. Configure Main Settings

Edit `config.ini` to set your preferred LLM provider and model:

```ini
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:14b
provider_server_address = 127.0.0.1:11434
```

### 5. Pull Required Models (for Ollama)

```bash
ollama pull deepseek-r1:14b
```

## Running AgenticSeek

### CLI Mode

The command-line interface for direct interaction:

```bash
source agentic_seek_env/bin/activate
python3 cli.py
```

### Web Mode

The web interface with FastAPI backend and React frontend:

```bash
python3 api.py
```

Then visit `http://localhost:3000` in your browser.

### Docker Services

For full web UI, search, and caching services:

```bash
# Linux/Mac
sudo ./start_services.sh

# Windows
start ./start_services.cmd
```

This starts:
- **Redis** - Caching and message queue
- **SearxNG** - Private web search (port 8080)
- **Frontend** - React web UI (port 3000)

## Configuration

See the [Configuration Guide](Configuration) for detailed settings.

### Quick Config Reference

| Setting | Description | Example |
|---------|-------------|---------|
| `is_local` | Use local LLM | `True` or `False` |
| `provider_name` | LLM provider | `ollama`, `lm-studio`, `openai` |
| `provider_model` | Model name | `deepseek-r1:14b` |
| `speak` | Enable text-to-speech | `True` or `False` |
| `listen` | Enable speech-to-text | `True` or `False` |
| `headless_browser` | Run browser headless | `True` or `False` |

## Supported LLM Providers

| Provider | Local | Setup |
|----------|-------|-------|
| **ollama** | Yes | Install Ollama, pull model |
| **lm-studio** | Yes | Install LM Studio |
| **openai** | No | Set `OPENAI_API_KEY` |
| **deepseek** | No | Set `DEEPSEEK_API_KEY` |
| **google** | No | Set Google API key |
| **huggingface** | No | Set HuggingFace token |
| **openrouter** | No | Set `OPENROUTER_API_KEY` |

## First Run

1. Start AgenticSeek using your preferred mode
2. Enter a query like "What's the weather today?" or "Write a Python script to sort a list"
3. The system will automatically route your query to the appropriate agent
4. For voice mode, enable `speak = True` and `listen = True` in config.ini

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Model not found | Run `ollama pull <model-name>` |
| Connection refused | Check that Ollama/server is running on the configured address |
| Browser fails | Install Chrome/Chromium and set `headless_browser = True` |
| Search not working | Ensure SearxNG is running: `docker ps` |

### Logs

Logs are configured in `config.ini` and can be found in the `logs/` directory (if configured).

## Next Steps

- Read the [Architecture Guide](Architecture) to understand the system design
- Explore the [Agents Guide](Agents) to learn about different agent capabilities
- Check the [Tools Guide](Tools) to understand available tools
- Read the [Development Guide](Development-Guide) to contribute
