# Development Guide

This guide covers development setup, conventions, and contribution processes for AgenticSeek.

## Development Setup

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/agenticSeek.git
cd agenticSeek

# Create virtual environment
python3 -m venv agentic_seek_env
source agentic_seek_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (if available)
pip install -r requirements-dev.txt
```

### 2. Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_browser_agent_parsing.py

# Run with coverage
python -m pytest tests/ --cov=sources
```

### 3. Pre-commit Hooks (if configured)

```bash
pip install pre-commit
pre-commit install
```

## Project Structure

```
agenticSeek/
├── sources/              # Main source code
│   ├── agents/           # AI agent implementations
│   │   ├── agent.py      # Base agent class
│   │   ├── casual_agent.py
│   │   ├── code_agent.py
│   │   ├── browser_agent.py
│   │   ├── file_agent.py
│   │   ├── planner_agent.py
│   │   └── mcp_agent.py
│   ├── tools/            # Tool implementations
│   │   ├── tools.py      # Base tool class
│   │   ├── PyInterpreter.py
│   │   ├── BashInterpreter.py
│   │   └── ...
│   ├── interaction.py    # User interaction handler
│   ├── llm_provider.py   # LLM provider abstraction
│   ├── router.py         # Agent selection router
│   ├── memory.py         # Conversation memory
│   └── ...
├── prompts/              # Agent prompt templates
│   ├── base/             # Base personality
│   └── jarvis/           # Jarvis personality
├── frontend/             # React frontend
├── llm_router/           # ML routing model
├── llm_server/           # Remote LLM server
├── tests/                # Unit tests
└── docs/                 # Documentation
```

## Coding Conventions

### Python Style

- Follow **PEP 8** guidelines
- Use **4 spaces** for indentation
- Maximum line length: **120 characters**
- Use **type hints** where practical

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `BaseAgent`, `PyInterpreter` |
| Functions/Methods | snake_case | `execute_tool()`, `process_response()` |
| Variables | snake_case | `provider_name`, `work_dir` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private Members | Leading underscore | `_internal_method()` |

### File Organization

```python
# Standard library imports
import os
import sys

# Third-party imports
import torch
from selenium import webdriver

# Local imports
from agents.agent import BaseAgent
from tools.tools import Tool

# Module code
class MyAgent(BaseAgent):
    """Agent documentation string."""

    def __init__(self, provider, memory, tools, config):
        super().__init__(provider, memory, tools, config)
        self.name = "MyAgent"

    def run(self, query):
        """Main execution method."""
        pass
```

### Docstrings

Use Google-style docstrings:

```python
def execute_tool(self, tool_name: str, content: str) -> str:
    """Execute a tool and return the output.

    Args:
        tool_name: Name of the tool to execute.
        content: Content to pass to the tool.

    Returns:
        Tool output as string.

    Raises:
        ToolError: If tool execution fails.
    """
    pass
```

## Adding New Features

### Adding a New Agent

1. **Create agent file** in `sources/agents/`:

```python
# sources/agents/my_agent.py
from agents.agent import BaseAgent

class MyAgent(BaseAgent):
    """Custom agent description."""

    def __init__(self, provider, memory, tools, config):
        super().__init__(provider, memory, tools, config)
        self.name = "MyAgent"

    def run(self, query):
        """Handle query."""
        # Implementation
        pass
```

2. **Create prompt files**:
   - `prompts/base/my_agent.txt`
   - `prompts/jarvis/my_agent.txt`

3. **Register in router** (`sources/router.py`):

```python
AGENT_CATEGORIES = {
    "casual": "CasualAgent",
    "coding": "CoderAgent",
    "browsing": "BrowserAgent",
    "files": "FileAgent",
    "my_category": "MyAgent",  # Add here
}
```

4. **Add tests** in `tests/test_my_agent.py`

### Adding a New Tool

1. **Create tool file** in `sources/tools/`:

```python
# sources/tools/my_tool.py
from tools.tools import Tool

class MyTool(Tool):
    """Custom tool description."""

    def __init__(self, config):
        super().__init__(config)
        self.name = "my_tool"

    def execute(self, query):
        """Execute tool logic."""
        # Implementation
        return result
```

2. **Register in agent**:

```python
from tools.my_tool import MyTool

tools = [
    PyInterpreter(config),
    MyTool(config),  # Add here
]
```

3. **Add tests** in `tests/test_my_tool.py`

### Adding a New LLM Provider

1. **Update** `sources/llm_provider.py`:

```python
class LLMProvider:
    def __init__(self, config):
        self.provider_name = config.get("provider_name")
        # Add new provider handler
        if self.provider_name == "my_provider":
            self.client = self._init_my_provider(config)

    def _init_my_provider(self, config):
        # Provider initialization
        pass
```

2. **Add configuration** support in `config.ini`

3. **Test** with respective API

## Testing

### Test Structure

```python
# tests/test_example.py
import pytest
from sources.agents.casual_agent import CasualAgent

class TestCasualAgent:
    """Test suite for CasualAgent."""

    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = CasualAgent(provider, memory, tools, config)
        assert agent.name == "CasualAgent"

    def test_simple_response(self):
        """Test simple query handling."""
        response = agent.run("Hello")
        assert isinstance(response, str)
        assert len(response) > 0
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_memory.py

# Specific test
pytest tests/test_memory.py::TestMemory::test_save_load

# With verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov=sources --cov-report=html
```

### Existing Tests

| Test File | Coverage |
|-----------|----------|
| `test_browser_agent_parsing.py` | Browser agent parsing logic |
| `test_memory.py` | Conversation memory |
| `test_provider.py` | LLM provider |
| `test_searx_search.py` | SearxNG search |
| `test_tools_parsing.py` | Tool block parsing |

## Git Workflow

### Branch Strategy

```
main (stable)
  └── develop (integration)
        └── feature/my-feature (development)
        └── fix/bug-fix (bug fixes)
```

### Commit Messages

Use conventional commits:

```
feat: add new agent routing strategy
fix: resolve browser timeout issue
docs: update configuration guide
test: add tests for memory module
refactor: simplify tool execution
```

### Pull Request Process

1. **Create feature branch** from `main`
2. **Make changes** with tests
3. **Run tests** locally
4. **Submit PR** with description:
   - What changed
   - Why it changed
   - How to test it
5. **Address review** comments
6. **Merge** after approval

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Common Debug Scenarios

| Issue | Debug Approach |
|-------|----------------|
| Agent not routing | Check router classification output |
| Tool not executing | Verify tool block parsing |
| LLM timeout | Check provider address and model |
| Browser fails | Check Chrome/Chromium installation |

### Using Python Debugger

```python
import pdb; pdb.set_trace()  # Breakpoint
```

## Performance Optimization

### LLM Response Time

- Use smaller models for faster responses
- Enable response streaming
- Cache common responses

### Memory Management

- Clear conversation history periodically
- Use `save_session = False` for memory-constrained systems

### Browser Optimization

- Use `headless_browser = True`
- Enable `stealth_mode` only when needed
- Reuse browser instances

## Documentation

### Wiki Pages

Keep wiki pages updated:
- [Home](Home) - Overview
- [Getting Started](Getting-Started) - Setup guide
- [Architecture](Architecture) - System design
- [Configuration](Configuration) - Settings
- [Agents](Agents) - Agent documentation
- [Tools](Tools) - Tool documentation
- [Development Guide](Development-Guide) - This page

### Code Documentation

- Docstrings for all public methods
- Inline comments for complex logic
- README updates for new features

## Release Process

1. **Update version** in `setup.py`
2. **Update CHANGELOG**
3. **Run full test suite**
4. **Create release tag**
5. **Build and publish** (if applicable)

## Contributing

1. **Fork** the repository
2. **Create feature branch**
3. **Make changes** with tests
4. **Submit pull request**
5. **Address review** feedback

See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) for detailed guidelines.

## Code of Conduct

See [CODE_OF_CONDUCT.md](../docs/CODE_OF_CONDUCT.md) for community guidelines.
