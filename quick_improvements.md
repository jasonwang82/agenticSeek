# AgenticSeek 快速改进指南

本文档列出了可以立即实施的改进，无需大规模重构。

## 1. 立即可修复的安全问题

### 1.1 添加基本输入验证
在 `api.py` 中添加输入长度限制：

```python
from pydantic import BaseModel, Field, validator

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    
    @validator('query')
    def validate_query(cls, v):
        # 移除潜在的危险字符
        dangerous_chars = ['<script>', '</script>', 'javascript:', 'onclick=']
        for char in dangerous_chars:
            if char.lower() in v.lower():
                raise ValueError(f"Potentially dangerous content detected")
        return v.strip()
```

### 1.2 限制命令执行
在 `sources/agents/code_agent.py` 中添加简单的命令过滤：

```python
BLOCKED_COMMANDS = ['rm -rf /', 'dd if=/dev/zero', 'mkfs', ':(){ :|:& };:']

def is_safe_command(command: str) -> bool:
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            return False
    return True
```

## 2. 性能快速优化

### 2.1 添加简单缓存
为 Router 添加决策缓存：

```python
from functools import lru_cache
import hashlib

class AgentRouter:
    @lru_cache(maxsize=128)
    def _cached_route_decision(self, query_hash: str):
        # 缓存路由决策
        return self._original_select_agent(query_hash)
    
    def select_agent(self, text: str) -> Agent:
        # 计算查询的哈希值
        query_hash = hashlib.md5(text.encode()).hexdigest()
        return self._cached_route_decision(query_hash)
```

### 2.2 减少重复的模型加载
在 `sources/router.py` 中优化：

```python
class AgentRouter:
    _shared_pipelines = None
    
    @classmethod
    def get_shared_pipelines(cls):
        if cls._shared_pipelines is None:
            cls._shared_pipelines = {
                "bart": pipeline("zero-shot-classification", 
                                model="facebook/bart-large-mnli",
                                device=0 if torch.cuda.is_available() else -1)
            }
        return cls._shared_pipelines
    
    def __init__(self, agents: list, supported_language: List[str] = ["en", "fr", "zh"]):
        self.agents = agents
        self.pipelines = self.get_shared_pipelines()  # 使用共享的 pipeline
```

## 3. 日志改进

### 3.1 统一日志格式
创建 `sources/logging_config.py`：

```python
import logging
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # 文件处理器
    file_handler = logging.FileHandler(f"logs/agenticseek_{datetime.now():%Y%m%d}.log")
    file_handler.setLevel(logging.DEBUG)
    
    # 设置格式
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 配置根日志器
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler, file_handler]
    )
```

### 3.2 添加请求追踪
在 `api.py` 中添加请求 ID：

```python
import uuid
from fastapi import Request

@api.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # 记录请求
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response
```

## 4. 错误处理改进

### 4.1 全局异常处理器
在 `api.py` 中添加：

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@api.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"Request {request_id} failed: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if api.debug else "An error occurred",
            "request_id": request_id
        }
    )
```

### 4.2 优雅的降级处理
在 `sources/llm_provider.py` 中：

```python
class Provider:
    def respond(self, history, verbose=True):
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return self._original_respond(history, verbose)
            except ConnectionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # 降级到简单响应
                    return "I'm having trouble connecting to the AI service. Please try again later."
```

## 5. 配置文件优化

### 5.1 添加配置验证
创建 `sources/config_validator.py`：

```python
import configparser
from pathlib import Path

def validate_config(config_path: str = "config.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    
    errors = []
    
    # 验证必需的部分
    required_sections = ['MAIN', 'BROWSER']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")
    
    # 验证路径
    if 'MAIN' in config and 'work_dir' in config['MAIN']:
        work_dir = Path(config['MAIN']['work_dir'])
        if not work_dir.exists():
            errors.append(f"Work directory does not exist: {work_dir}")
    
    # 验证布尔值
    boolean_fields = [
        ('MAIN', 'is_local'),
        ('MAIN', 'speak'),
        ('BROWSER', 'headless_browser')
    ]
    
    for section, field in boolean_fields:
        if section in config and field in config[section]:
            value = config[section][field].lower()
            if value not in ['true', 'false']:
                errors.append(f"Invalid boolean value for {section}.{field}: {value}")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    return config
```

## 6. 资源清理

### 6.1 浏览器资源管理
在 `sources/browser.py` 中添加：

```python
import atexit
from contextlib import contextmanager

class Browser:
    def __init__(self, driver, **kwargs):
        self.driver = driver
        # 注册清理函数
        atexit.register(self.cleanup)
    
    def cleanup(self):
        """清理浏览器资源"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            logger.error(f"Error cleaning up browser: {e}")
    
    @contextmanager
    def temporary_tab(self):
        """临时标签页上下文管理器"""
        original_tab = self.driver.current_window_handle
        self.driver.execute_script("window.open('');")
        new_tab = self.driver.window_handles[-1]
        self.driver.switch_to.window(new_tab)
        
        try:
            yield
        finally:
            self.driver.close()
            self.driver.switch_to.window(original_tab)
```

### 6.2 内存泄漏预防
定期清理大对象：

```python
class Agent:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._message_history_limit = 100
    
    def add_to_history(self, message):
        self.message_history.append(message)
        # 限制历史记录大小
        if len(self.message_history) > self._message_history_limit:
            self.message_history = self.message_history[-self._message_history_limit:]
```

## 7. 开发体验改进

### 7.1 添加类型注解
示例改进：

```python
from typing import List, Dict, Optional, Union

def select_agent(self, text: str) -> Optional[Agent]:
    """选择合适的代理处理文本"""
    pass

def respond(self, history: List[Dict[str, str]], verbose: bool = True) -> str:
    """生成响应"""
    pass
```

### 7.2 改进的错误消息
替换通用错误消息：

```python
# 原代码
raise Exception("Error occurred")

# 改进后
raise ValueError(f"Invalid provider name: '{provider_name}'. "
                f"Available providers: {', '.join(self.available_providers.keys())}")
```

## 8. 快速修复清单

- [ ] 在所有用户输入点添加长度验证
- [ ] 为所有文件操作添加 try-except 块
- [ ] 将硬编码的端口号移到配置文件
- [ ] 添加 API 速率限制
- [ ] 实现基本的健康检查端点
- [ ] 为长时间运行的操作添加超时
- [ ] 清理未使用的导入和死代码
- [ ] 统一错误响应格式
- [ ] 添加基本的 CORS 配置验证
- [ ] 实现优雅关闭机制

## 实施建议

1. **今天可以完成的**：
   - 输入验证
   - 日志格式统一
   - 基本错误处理

2. **本周可以完成的**：
   - 资源清理
   - 配置验证
   - 简单缓存

3. **需要测试的改进**：
   - 命令过滤
   - 并发处理
   - 内存管理

这些改进可以显著提高系统的稳定性和安全性，而无需进行大规模重构。建议按照优先级逐步实施，并在每次改进后进行充分测试。