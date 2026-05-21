# Architecture

This document describes the system architecture of AgenticSeek.

## System Overview

AgenticSeek uses a **multi-agent architecture** with intelligent routing to handle different types of tasks. The system is designed to be fully local, with all data processing happening on the user's device.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Entry Points                              │
│                   cli.py (CLI) | api.py (Web)                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Interaction Module                            │
│          (User I/O, Voice, Router Selection)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Router                                  │
│     (Selects best agent based on query classification)          │
│     - Facebook BART model (zero-shot classification)            │
│     - Adaptive LLM router model                                  │
│     - Complexity estimation (LOW/HIGH)                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  CasualAgent │    │  CoderAgent  │    │  BrowserAgent│
│   (Talk)     │    │   (Code)     │    │    (Web)     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        │                   ▼                   │
        │           ┌──────────────┐            │
        │           │   Tools      │◄───────────┘
        │           │ - PyInterpreter
        │           │ - BashInterpreter
        │           │ - C/Go/Java
        │           └──────────────┘
        │                   │
        └───────┬───────────┘
                ▼
┌─────────────────────────────────────────────────────────────────┐
│              PlannerAgent (Complex Tasks)                        │
│  - Parses JSON plan from LLM                                     │
│  - Orchestrates sub-agents                                      │
│  - Updates plan dynamically based on results                    │
└─────────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Provider                                  │
│   Ollama | LM Studio | OpenAI | DeepSeek | Google | HuggingFace │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Entry Points

| File | Purpose |
|------|---------|
| `cli.py` | Command-line interface for terminal interaction |
| `api.py` | FastAPI web server for web interface |

### 2. Interaction Module

**File:** `sources/interaction.py`

Handles user input/output, including:
- Text input parsing
- Voice input (speech-to-text)
- Voice output (text-to-speech)
- Router selection coordination

### 3. Agent Router

**File:** `sources/router.py`

Intelligently routes user queries to the most appropriate agent:
- **Query Classification**: Uses Facebook BART model for zero-shot classification
- **Adaptive Routing**: ML-based router model for dynamic agent selection
- **Complexity Estimation**: Determines if a task is LOW or HIGH complexity

#### Agent Categories

| Category | Description | Target Agent |
|----------|-------------|--------------|
| Casual | General conversation, chit-chat | CasualAgent |
| Coding | Programming tasks, scripts | CoderAgent |
| Browsing | Web search, information retrieval | BrowserAgent |
| Files | File operations, search | FileAgent |
| Complex | Multi-step tasks | PlannerAgent |

### 4. Agents

**Directory:** `sources/agents/`

| Agent | File | Role |
|-------|------|------|
| **BaseAgent** | `agent.py` | Abstract base class for all agents |
| **CasualAgent** | `casual_agent.py` | General conversation |
| **CoderAgent** | `code_agent.py` | Code writing and execution |
| **BrowserAgent** | `browser_agent.py` | Web browsing and search |
| **FileAgent** | `file_agent.py` | File operations |
| **PlannerAgent** | `planner_agent.py` | Complex task orchestration |
| **McpAgent** | `mcp_agent.py` | MCP protocol integration (WIP) |

### 5. Tools

**Directory:** `sources/tools/`

Tools are executed using a **block-based** pattern:

```
LLM generates:
```tool_name
code_or_query
```

System:
1. Extracts tool name and content
2. Executes the tool
3. Returns feedback to LLM
4. LLM processes feedback
```

#### Available Tools

| Tool | File | Purpose |
|------|------|---------|
| **PyInterpreter** | `PyInterpreter.py` | Execute Python code |
| **BashInterpreter** | `BashInterpreter.py` | Execute shell commands |
| **C_Interpreter** | `C_Interpreter.py` | Compile and run C code |
| **GoInterpreter** | `GoInterpreter.py` | Compile and run Go code |
| **JavaInterpreter** | `JavaInterpreter.py` | Compile and run Java code |
| **FileFinder** | `fileFinder.py` | File search and operations |
| **WebSearch** | `webSearch.py` | General web search |
| **SearxSearch** | `searxSearch.py` | SearxNG private search |
| **McpFinder** | `mcpFinder.py` | MCP-based search (WIP) |

### 6. LLM Provider

**File:** `sources/llm_provider.py`

Abstracts LLM communication behind a unified interface:

| Provider | Implementation |
|----------|----------------|
| Ollama | Direct Ollama API |
| LM Studio | OpenAI-compatible API |
| OpenAI | OpenAI API |
| DeepSeek | DeepSeek API |
| Google | Gemini API |
| HuggingFace | HuggingFace API |
| Together | TogetherAI API |
| OpenRouter | OpenRouter API |

### 7. Supporting Modules

| Module | File | Purpose |
|--------|------|---------|
| **Memory** | `sources/memory.py` | Conversation history management |
| **Language** | `sources/language.py` | Language detection and translation |
| **Speech-to-Text** | `sources/speech_to_text.py` | Voice input processing |
| **Text-to-Speech** | `sources/text_to_speech.py` | Voice output processing |
| **Browser** | `sources/browser.py` | Selenium browser automation |
| **Logger** | `sources/logger.py` | Logging utilities |
| **Schemas** | `sources/schemas.py` | Data models and types |
| **Utility** | `sources/utility.py` | Common utilities |

## Data Flow

### Simple Query Flow

```
User Query → Interaction → Router → Agent → LLM → Response → User
```

### Complex Query Flow (PlannerAgent)

```
User Query → Interaction → Router → PlannerAgent
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                         Sub-Agent 1  Sub-Agent 2  Sub-Agent 3
                              │           │           │
                              └───────────┼───────────┘
                                          ▼
                                    Aggregated Result
                                          │
                                          ▼
                                     User Response
```

### Tool Execution Flow

```
LLM → Tool Block → Extract → Execute → Feedback → LLM → Continue or Done
```

## Prompt System

**Directory:** `prompts/`

The prompt system supports multiple personalities:

| Personality | Directory | Description |
|-------------|-----------|-------------|
| **Base** | `prompts/base/` | Standard AI assistant personality |
| **Jarvis** | `prompts/jarvis/` | Jarvis-like personality |

Each personality has agent-specific prompt files:
- `casual_agent.txt`
- `coder_agent.txt`
- `browser_agent.txt`
- `file_agent.txt`
- `planner_agent.txt`
- `mcp_agent.txt`

## Configuration Files

| File | Purpose |
|------|---------|
| `config.ini` | Main configuration (provider, model, features) |
| `.env` | Environment variables (API keys, URLs) |
| `docker-compose.yml` | Docker services definition |
| `searxng/settings.yml` | SearxNG search configuration |

## Deployment Architecture

### Docker Services

```yaml
services:
  redis:       # Caching and message queue
  searxng:     # Private web search (port 8080)
  frontend:    # React web UI (port 3000)
```

### Local Services

| Service | Port | Purpose |
|---------|------|---------|
| Ollama | 11434 | Local LLM server |
| SearxNG | 8080 | Web search engine |
| FastAPI | varies | Backend API |
| React | 3000 | Frontend UI |
| Redis | 6379 | Message queue/cache |
