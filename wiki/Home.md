# AgenticSeek Wiki

Welcome to the AgenticSeek project documentation wiki.

## About

**AgenticSeek** is a **100% local alternative to Manus AI** - a voice-enabled AI assistant that autonomously browses the web, writes code, plans tasks, and manages files while keeping all data on the user's device.

## Key Features

- **Fully Local & Private** - No data sharing, all processing happens on your hardware
- **Smart Web Browsing** - Search, read, extract information, and fill forms automatically
- **Autonomous Coding** - Support for Python, C, Go, Java, Bash, and more
- **Smart Agent Selection** - Automatic routing to the best agent for each task
- **Complex Task Planning** - Splits complex tasks into steps using multiple AI agents
- **Voice-Enabled** - Built-in text-to-speech and speech-to-text capabilities

## Quick Links

| Document | Description |
|----------|-------------|
| [Getting Started](Getting-Started) | Installation and setup guide |
| [Architecture](Architecture) | System architecture and components |
| [Configuration](Configuration) | Configuration options and settings |
| [Agents](Agents) | Agent system documentation |
| [Tools](Tools) | Tool system documentation |
| [Development Guide](Development-Guide) | Contributing and development |

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.10+ |
| **Frontend** | React 19 |
| **LLM Providers** | Ollama, LM Studio, OpenAI-compatible APIs |
| **Web Framework** | FastAPI |
| **Task Queue** | Celery + Redis/Valkey |
| **Web Search** | SearxNG (self-hosted) |
| **Browser Automation** | Selenium |

## Hardware Requirements

| Model Size | GPU VRAM | Usability |
|------------|----------|-----------|
| 7B | 8GB | Not recommended |
| 14B | 12GB (RTX 3060) | Usable for simple tasks |
| 32B | 24GB+ (RTX 4090) | Most tasks successful |
| 70B+ | 48GB+ | Excellent, recommended |

## Project Structure

```
agenticSeek/
├── sources/              # Main source code
│   ├── agents/           # AI agent implementations
│   ├── tools/            # Tool implementations
│   └── ...
├── frontend/             # React frontend
├── prompts/              # Agent prompt templates
├── llm_router/           # ML routing model
├── llm_server/           # Remote LLM server
├── searxng/              # SearxNG configuration
├── tests/                # Unit tests
└── docs/                 # Documentation
```

## License

This project is open source. See the [LICENSE](../LICENSE) file for details.
