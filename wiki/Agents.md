# Agents

This document describes the agent system in AgenticSeek.

## Overview

AgenticSeek uses a **multi-agent architecture** where specialized agents handle different types of tasks. An intelligent router automatically selects the best agent based on the user's query.

## Agent Hierarchy

```
                    ┌─────────────┐
                    │   Router    │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ CasualAgent  │ │CoderAgent│ │ BrowserAgent │
    └──────────────┘ └──────────┘ └──────────────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                    ┌──────┴──────┐
                    │ FileAgent   │
                    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │PlannerAgent │
                    └─────────────┘
```

## Base Agent

**File:** `sources/agents/agent.py`

The `BaseAgent` class provides the foundation for all agents:

- Common initialization (LLM provider, memory, tools)
- Message handling and formatting
- Tool execution framework
- Prompt loading

### Key Methods

| Method | Purpose |
|--------|---------|
| `__init__()` | Initialize agent with provider, memory, tools |
| `run()` | Main execution loop |
| `process_response()` | Parse and handle LLM response |
| `execute_tool()` | Run a tool block |

## CasualAgent

**File:** `sources/agents/casual_agent.py`

**Purpose:** General conversation and chit-chat.

### Capabilities

- Natural conversation
- Answering general knowledge questions
- Casual discussion

### Tools

None. The CasualAgent relies solely on the LLM's knowledge.

### Example Interactions

```
User: "How are you today?"
CasualAgent: "I'm doing well, thank you for asking!"

User: "What's your favorite color?"
CasualAgent: "I don't have personal preferences, but I find blue quite appealing in design."
```

## CoderAgent

**File:** `sources/agents/code_agent.py`

**Purpose:** Code writing, execution, and debugging.

### Capabilities

- Write code in multiple languages
- Execute and test code
- Debug errors iteratively
- Explain code

### Supported Languages

| Language | Tool | Execution |
|----------|------|-----------|
| Python | PyInterpreter | Direct execution |
| Bash | BashInterpreter | Shell execution |
| C | C_Interpreter | Compile and run |
| Go | GoInterpreter | Compile and run |
| Java | JavaInterpreter | Compile and run |

### Tool Usage Pattern

```
CoderAgent receives coding task
    ↓
Generates code in tool block
    ↓
```python
def hello():
    print("Hello, World!")
```
    ↓
PyInterpreter extracts and executes
    ↓
Returns output to CoderAgent
    ↓
Agent processes result and responds
```

### Example Interactions

```
User: "Write a Python function to sort a list using bubble sort"
CoderAgent: ```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
```
Let me test this:
```python
print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))
```
Output: [11, 12, 22, 25, 34, 64, 90]
The bubble sort function works correctly!
```

## BrowserAgent

**File:** `sources/agents/browser_agent.py`

**Purpose:** Web browsing, search, and information retrieval.

### Capabilities

- Web search via SearxNG
- Direct URL browsing
- Content extraction
- Form filling
- Information synthesis

### Tools

| Tool | Purpose |
|------|---------|
| WebSearch | General web search |
| SearxSearch | Private search via SearxNG |
| Browser | Selenium-based browser automation |

### Browser Automation

The BrowserAgent uses Selenium with optional stealth mode:

```ini
[BROWSER]
headless_browser = True
stealth_mode = False
```

### Example Interactions

```
User: "What's the latest news about AI?"
BrowserAgent: Let me search for that.
```searx_search
latest AI news 2024
```
Here are the top results:
1. [Article title] - [Source]
2. [Article title] - [Source]
...
```

## FileAgent

**File:** `sources/agents/file_agent.py`

**Purpose:** File operations and management.

### Capabilities

- File search
- File reading and writing
- Directory operations
- File content analysis

### Tools

| Tool | Purpose |
|------|---------|
| FileFinder | Search and locate files |

### Example Interactions

```
User: "Find all Python files in the current directory"
FileAgent: ```file_finder
*.py
```
Found 5 Python files:
- main.py
- utils.py
- config.py
- test_main.py
- test_utils.py
```

## PlannerAgent

**File:** `sources/agents/planner_agent.py`

**Purpose:** Complex multi-step task orchestration.

### Capabilities

- Parse complex requests
- Break down into sub-tasks
- Orchestrate multiple agents
- Aggregate results
- Dynamic plan adjustment

### How It Works

1. **Receive complex query**
2. **Generate JSON plan** with steps and assigned agents
3. **Execute steps** using appropriate agents
4. **Aggregate results**
5. **Update plan** if needed based on intermediate results
6. **Return final answer**

### Plan Structure

```json
{
  "plan": [
    {
      "step": 1,
      "action": "search for information",
      "agent": "BrowserAgent",
      "expected_output": "research data"
    },
    {
      "step": 2,
      "action": "analyze data and write summary",
      "agent": "CoderAgent",
      "expected_output": "analysis code"
    },
    {
      "step": 3,
      "action": "compile final report",
      "agent": "CasualAgent",
      "expected_output": "formatted report"
    }
  ]
}
```

### Example Interactions

```
User: "Research the best Python web frameworks in 2024, compare their performance, and create a summary table"

PlannerAgent breaks this down:
1. BrowserAgent: Search for Python web frameworks
2. BrowserAgent: Research performance benchmarks
3. CoderAgent: Create comparison script
4. CasualAgent: Format summary table
```

## McpAgent (Work in Progress)

**File:** `sources/agents/mcp_agent.py`

**Purpose:** Model Context Protocol (MCP) integration.

### Status

Under development. Will provide:
- MCP server communication
- External tool discovery
- Standardized tool execution

## Agent Routing

The router automatically selects agents based on query classification.

### Routing Methods

| Method | Description |
|--------|-------------|
| **BART Classification** | Facebook BART model for zero-shot classification |
| **Adaptive Router** | ML-based router model for dynamic selection |
| **Complexity Estimation** | LOW vs HIGH complexity determination |

### Routing Categories

| Category | Target Agent | Example Queries |
|----------|--------------|-----------------|
| Casual | CasualAgent | "How are you?", "Tell me a joke" |
| Coding | CoderAgent | "Write a Python script", "Fix this bug" |
| Browsing | BrowserAgent | "Search for...", "What's on this website" |
| Files | FileAgent | "Find files...", "Read this file" |
| Complex | PlannerAgent | "Research and compare...", "Build a complete..." |

### Router Configuration

```ini
[MAIN]
use_adaptive_router = True
```

## Prompt System

Each agent has dedicated prompt files that define its behavior and personality.

### Prompt Structure

```
prompts/
├── base/
│   ├── casual_agent.txt
│   ├── coder_agent.txt
│   ├── browser_agent.txt
│   ├── file_agent.txt
│   ├── planner_agent.txt
│   └── mcp_agent.txt
└── jarvis/
    ├── casual_agent.txt
    ├── coder_agent.txt
    ├── browser_agent.txt
    ├── file_agent.txt
    ├── planner_agent.txt
    └── mcp_agent.txt
```

### Switching Personalities

Set in `config.ini`:

```ini
[MAIN]
jarvis_personality = True   # Use Jarvis prompts
jarvis_personality = False  # Use Base prompts
```

## Adding Custom Agents

To create a new agent:

1. **Inherit from BaseAgent**
2. **Implement required methods**
3. **Create prompt file** in `prompts/base/` and `prompts/jarvis/`
4. **Register in router** with classification category
5. **Add tools** as needed

### Example

```python
from agents.agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, provider, memory, tools, config):
        super().__init__(provider, memory, tools, config)
        self.name = "CustomAgent"

    def run(self, query):
        # Custom implementation
        pass
```
