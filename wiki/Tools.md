# Tools

This document describes the tool system in AgenticSeek.

## Overview

AgenticSeek uses a **block-based tool execution** system. Agents generate tool blocks in their responses, which the system extracts, executes, and returns as feedback to the agent.

## Tool Execution Flow

```
Agent generates response with tool block
        ↓
System extracts tool block
        ↓
Execute tool with extracted content
        ↓
Return output to agent
        ↓
Agent processes output and continues
```

## Tool Block Syntax

Tools are invoked using markdown code blocks:

````
```tool_name
content_or_query
```
````

### Example

````
```python
def hello():
    print("Hello, World!")
```
````

## Available Tools

### Code Execution Tools

#### PyInterpreter

**File:** `sources/tools/PyInterpreter.py`

**Purpose:** Execute Python code.

**Usage:**
````
```python
import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

print(calculate_circle_area(5))
```
````

**Output:**
```
78.53981633974483
```

**Features:**
- Full Python execution environment
- Access to standard library
- Captures stdout output
- Error reporting

---

#### BashInterpreter

**File:** `sources/tools/BashInterpreter.py`

**Purpose:** Execute shell commands.

**Usage:**
````
```bash
ls -la /home
```
````

**Output:**
```
total 16
drwxr-xr-x  4 root root 4096 Jan  1 00:00 .
drwxr-xr-x 20 root root 4096 Jan  1 00:00 ..
```

**Features:**
- Shell command execution
- Working directory context
- stdout and stderr capture
- Exit code tracking

---

#### C_Interpreter

**File:** `sources/tools/C_Interpreter.py`

**Purpose:** Compile and run C code.

**Usage:**
````
```c
#include <stdio.h>

int main() {
    printf("Hello from C!\n");
    return 0;
}
```
````

**Output:**
```
Hello from C!
```

**Features:**
- GCC compilation
- Execution of compiled binary
- Error capture for compile/runtime errors

---

#### GoInterpreter

**File:** `sources/tools/GoInterpreter.py`

**Purpose:** Compile and run Go code.

**Usage:**
````
```go
package main

import "fmt"

func main() {
    fmt.Println("Hello from Go!")
}
```
````

**Output:**
```
Hello from Go!
```

**Features:**
- Go compilation
- Execution of compiled binary
- Error reporting

---

#### JavaInterpreter

**File:** `sources/tools/JavaInterpreter.py`

**Purpose:** Compile and run Java code.

**Usage:**
````
```java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
```
````

**Output:**
```
Hello from Java!
```

**Features:**
- Javac compilation
- JVM execution
- Error capture

### Search Tools

#### WebSearch

**File:** `sources/tools/webSearch.py`

**Purpose:** General web search.

**Usage:**
````
```web_search
Python web frameworks 2024
```
````

**Output:**
```
1. Top 10 Python Web Frameworks in 2024 - [URL]
2. Best Python Frameworks for Web Development - [URL]
...
```

**Features:**
- General web search
- Returns formatted results with URLs

---

#### SearxSearch

**File:** `sources/tools/searxSearch.py`

**Purpose:** Private search via SearxNG.

**Usage:**
````
```searx_search
latest AI developments
```
````

**Output:**
```
1. [Title] - [Source URL]
   [Snippet text]
2. [Title] - [Source URL]
   [Snippet text]
...
```

**Features:**
- Privacy-focused search
- Multiple search engine aggregation
- Configurable via `searxng/settings.yml`
- Requires SearxNG instance running

**Configuration:**
```bash
# .env
SEARXNG_BASE_URL="http://127.0.0.1:8080"
```

### File Tools

#### FileFinder

**File:** `sources/tools/fileFinder.py`

**Purpose:** File search and operations.

**Usage:**
````
```file_finder
*.py
```
````

**Output:**
```
Found files:
- /path/to/main.py
- /path/to/utils.py
- /path/to/config.py
```

**Features:**
- Glob pattern matching
- File content search
- Directory traversal
- Path filtering

### Browser Tools

#### Browser

**File:** `sources/browser.py`

**Purpose:** Selenium-based browser automation.

**Usage by BrowserAgent:**
- Navigate to URLs
- Extract page content
- Fill forms
- Click elements
- Take screenshots

**Features:**
- Full browser automation
- JavaScript execution
- Cookie management
- Screenshot capture

**Configuration:**
```ini
[BROWSER]
headless_browser = True
stealth_mode = False
```

### Experimental Tools

#### McpFinder

**File:** `sources/tools/mcpFinder.py`

**Purpose:** MCP-based search (under development).

**Status:** Work in progress. Will integrate with Model Context Protocol servers.

## Tool Base Class

**File:** `sources/tools/tools.py`

All tools inherit from a common base class that provides:

- Standard interface for execution
- Error handling
- Output formatting
- Logging

### Adding Custom Tools

1. **Create tool file** in `sources/tools/`
2. **Inherit from base Tool class**
3. **Implement `execute()` method**
4. **Register in agent's tool list**

### Example Custom Tool

```python
from tools.tools import Tool

class CustomTool(Tool):
    def __init__(self, config):
        super().__init__(config)
        self.name = "custom_tool"

    def execute(self, query):
        # Tool implementation
        result = self.process(query)
        return result

    def process(self, query):
        # Custom processing logic
        return f"Result for: {query}"
```

### Registering Tool

```python
from agents.agent import BaseAgent
from tools.custom_tool import CustomTool

# In agent initialization
tools = [
    PyInterpreter(config),
    BashInterpreter(config),
    CustomTool(config),  # Add custom tool
]
```

## Tool Usage by Agent

| Agent | Available Tools |
|-------|-----------------|
| **CasualAgent** | None |
| **CoderAgent** | PyInterpreter, BashInterpreter, C_Interpreter, GoInterpreter, JavaInterpreter |
| **BrowserAgent** | WebSearch, SearxSearch, Browser |
| **FileAgent** | FileFinder |
| **PlannerAgent** | Orchestrates other agents and their tools |
| **McpAgent** | McpFinder (WIP) |

## Tool Safety

### Execution Sandbox

- Code execution runs in subprocess context
- File operations are limited to configured `work_dir`
- Browser runs in headless mode by default

### Security Considerations

| Risk | Mitigation |
|------|------------|
| Arbitrary code execution | Expected behavior for coding agents |
| File system access | Limited to `work_dir` configuration |
| Network access | BrowserAgent has full access; configure firewall if needed |
| Resource exhaustion | No built-in limits; monitor system resources |

## Tool Output Format

Tools return formatted output that includes:

- **Success:** Tool output content
- **Error:** Error message with traceback
- **Timeout:** Timeout notification (if applicable)

### Error Example

```
Error executing python:
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'undefined_var' is not defined
```

## Debugging Tools

### Enable Verbose Logging

Set in `config.ini` or check log output:

```
[LOGGING]
level = DEBUG
```

### Test Tool Execution

```python
from tools.PyInterpreter import PyInterpreter

tool = PyInterpreter(config)
result = tool.execute("print('Hello')")
print(result)
```

## Tool Configuration

Some tools have specific configuration requirements:

### SearxSearch

Requires SearxNG instance:
```bash
docker compose up -d searxng
```

### Browser Tools

Requires Chrome/Chromium:
```bash
# Ubuntu
sudo apt install chromium-browser

# macOS
brew install chromedriver
```

### Code Interpreters

Require respective compilers/interpreters:
```bash
# Python (usually pre-installed)
python3 --version

# C compiler
gcc --version

# Go
go version

# Java
java -version
javac -version
```
