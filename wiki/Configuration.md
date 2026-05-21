# Configuration Guide

This document covers all configuration options for AgenticSeek.

## Main Configuration (config.ini)

The `config.ini` file is the primary configuration file.

### [MAIN] Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `is_local` | Boolean | `True` | Use local LLM (`True`) or cloud API (`False`) |
| `provider_name` | String | `ollama` | LLM provider name |
| `provider_model` | String | `deepseek-r1:14b` | Model identifier |
| `provider_server_address` | String | `127.0.0.1:11434` | LLM server address and port |
| `agent_name` | String | `AgenticSeek` | AI assistant name (used in TTS) |
| `recover_last_session` | Boolean | `False` | Restore previous conversation |
| `save_session` | Boolean | `False` | Save conversation to disk |
| `speak` | Boolean | `False` | Enable text-to-speech output |
| `listen` | Boolean | `False` | Enable speech-to-text input |
| `work_dir` | String | `/path/to/workspace` | Working directory for file operations |
| `jarvis_personality` | Boolean | `False` | Use Jarvis personality prompts |
| `languages` | String | `en` | Language code (en, zh, fr, ja, pt) |
| `use_adaptive_router` | Boolean | `True` | Use ML-based adaptive routing |

### [BROWSER] Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `headless_browser` | Boolean | `True` | Run browser in headless mode |
| `stealth_mode` | Boolean | `False` | Enable anti-detection mode |

### Example config.ini

```ini
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:14b
provider_server_address = 127.0.0.1:11434
agent_name = AgenticSeek
recover_last_session = True
save_session = True
speak = False
listen = False
work_dir = /Users/me/agentic-workspace
jarvis_personality = False
languages = en
use_adaptive_router = True

[BROWSER]
headless_browser = True
stealth_mode = False
```

## Environment Variables (.env)

The `.env` file stores sensitive configuration like API keys.

| Variable | Description | Required For |
|----------|-------------|--------------|
| `SEARXNG_BASE_URL` | SearxNG search engine URL | Web search features |
| `OPENAI_API_KEY` | OpenAI API key | OpenAI provider |
| `DEEPSEEK_API_KEY` | DeepSeek API key | DeepSeek provider |
| `OPENROUTER_API_KEY` | OpenRouter API key | OpenRouter provider |

### Example .env

```bash
SEARXNG_BASE_URL="http://127.0.0.1:8080"
OPENAI_API_KEY='sk-xxxxx'
DEEPSEEK_API_KEY='sk-xxxxx'
OPENROUTER_API_KEY='or-xxxxx'
```

## LLM Provider Configuration

### Ollama (Local)

```ini
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:14b
provider_server_address = 127.0.0.1:11434
```

**Setup:**
```bash
ollama pull deepseek-r1:14b
```

### LM Studio (Local)

```ini
[MAIN]
is_local = True
provider_name = lm-studio
provider_model = your-model-name
provider_server_address = 127.0.0.1:1234
```

### OpenAI (Cloud)

```ini
[MAIN]
is_local = False
provider_name = openai
provider_model = gpt-4
provider_server_address = https://api.openai.com
```

**.env:**
```bash
OPENAI_API_KEY='sk-xxxxx'
```

### DeepSeek (Cloud)

```ini
[MAIN]
is_local = False
provider_name = deepseek
provider_model = deepseek-chat
```

**.env:**
```bash
DEEPSEEK_API_KEY='sk-xxxxx'
```

### Google Gemini (Cloud)

```ini
[MAIN]
is_local = False
provider_name = google
provider_model = gemini-pro
```

### HuggingFace (Cloud)

```ini
[MAIN]
is_local = False
provider_name = huggingface
provider_model = your-model-name
```

### OpenRouter (Cloud)

```ini
[MAIN]
is_local = False
provider_name = openrouter
provider_model = your-model-name
```

**.env:**
```bash
OPENROUTER_API_KEY='or-xxxxx'
```

## Docker Configuration

### docker-compose.yml

The Docker Compose file defines three services:

```yaml
services:
  redis:
    image: valkey/valkey:latest
    ports:
      - "6379:6379"

  searxng:
    image: searxng/searxng:latest
    ports:
      - "8080:8080"
    volumes:
      - ./searxng:/etc/searxng

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - redis
```

### Starting Docker Services

```bash
# Linux/Mac
sudo ./start_services.sh

# Windows
start ./start_services.cmd
```

## SearxNG Configuration

**File:** `searxng/settings.yml`

Key settings:
- Search engines enabled
- Rate limiting
- UI preferences
- Server binding

## Personality Configuration

AgenticSeek supports multiple assistant personalities.

### Available Personalities

| Personality | Directory | Description |
|-------------|-----------|-------------|
| **Base** | `prompts/base/` | Standard AI assistant |
| **Jarvis** | `prompts/jarvis/` | Jarvis-like personality |

### Switching Personality

Set `jarvis_personality` in `config.ini`:

```ini
[MAIN]
jarvis_personality = True   # Use Jarvis personality
jarvis_personality = False  # Use Base personality
```

## Language Configuration

Set the `languages` key in `config.ini`:

```ini
[MAIN]
languages = en    # English
languages = zh    # Chinese
languages = fr    # French
languages = ja    # Japanese
languages = pt    # Portuguese
```

## Session Configuration

### Save Sessions

```ini
[MAIN]
save_session = True
```

Saves conversation history to disk for later review.

### Recover Last Session

```ini
[MAIN]
recover_last_session = True
```

Automatically loads the previous session on startup.

## Voice Configuration

### Text-to-Speech

```ini
[MAIN]
speak = True
```

Enables voice output using the Kokoro TTS engine.

### Speech-to-Text

```ini
[MAIN]
listen = True
```

Enables voice input for hands-free interaction.

## Browser Configuration

### Headless Mode

```ini
[BROWSER]
headless_browser = True
```

Runs the browser without a visible window (recommended for servers).

### Stealth Mode

```ini
[BROWSER]
stealth_mode = True
```

Enables anti-detection measures for web scraping. Use responsibly.

## Hardware Recommendations

### Model Size vs VRAM

| Model Size | Minimum VRAM | Recommended GPU | Notes |
|------------|--------------|-----------------|-------|
| 7B | 8GB | GTX 1080 Ti | Not recommended, poor performance |
| 14B | 12GB | RTX 3060 | Usable for simple tasks |
| 32B | 24GB+ | RTX 4090 | Most tasks successful |
| 70B+ | 48GB+ | A100/RTX 6000 | Excellent, recommended |
