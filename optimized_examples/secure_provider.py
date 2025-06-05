"""
优化后的 Provider 实现示例
使用策略模式、更好的错误处理和资源管理
"""
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager
import httpx
from openai import AsyncOpenAI
import logging
from dataclasses import dataclass
from functools import lru_cache
import os
from cryptography.fernet import Fernet

# 配置数据类
@dataclass
class ProviderConfig:
    """Provider 配置"""
    name: str
    model: str
    server_address: str = "127.0.0.1:5000"
    is_local: bool = True
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

# 抽象基类
class LLMProviderInterface(ABC):
    """LLM Provider 接口定义"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """生成文本的抽象方法"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
    
    async def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """验证消息格式"""
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        for msg in messages:
            if not isinstance(msg, dict):
                raise ValueError(f"Invalid message format: {msg}")
            if 'role' not in msg or 'content' not in msg:
                raise ValueError(f"Message missing required fields: {msg}")
        
        return True

# Ollama 实现
class OllamaProvider(LLMProviderInterface):
    """Ollama Provider 实现"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = f"http://{config.server_address}"
        self._client = None
    
    @asynccontextmanager
    async def _get_client(self):
        """获取 HTTP 客户端"""
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            yield client
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """使用 Ollama 生成文本"""
        await self.validate_messages(messages)
        
        async with self._get_client() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.config.model,
                        "messages": messages,
                        "stream": False,
                        **kwargs
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # 模型不存在，尝试拉取
                    await self._pull_model()
                    # 重试
                    return await self.generate(messages, **kwargs)
                raise
            except Exception as e:
                self.logger.error(f"Ollama generation failed: {e}")
                raise
    
    async def _pull_model(self):
        """拉取模型"""
        self.logger.info(f"Pulling model {self.config.model}...")
        async with self._get_client() as client:
            response = await client.post(
                f"{self.base_url}/api/pull",
                json={"name": self.config.model}
            )
            response.raise_for_status()
    
    async def health_check(self) -> bool:
        """检查 Ollama 服务是否正常"""
        try:
            async with self._get_client() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

# OpenAI 实现
class OpenAIProvider(LLMProviderInterface):
    """OpenAI Provider 实现"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not config.api_key:
            raise ValueError("OpenAI provider requires an API key")
        
        base_url = f"http://{config.server_address}" if config.is_local else None
        self.client = AsyncOpenAI(api_key=config.api_key, base_url=base_url)
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """使用 OpenAI 生成文本"""
        await self.validate_messages(messages)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """检查 OpenAI 服务是否正常"""
        try:
            models = await self.client.models.list()
            return bool(models.data)
        except Exception:
            return False

# 安全的 API 密钥管理器
class SecureAPIKeyManager:
    """安全的 API 密钥管理"""
    
    def __init__(self, key_file: str = ".keys/master.key"):
        self.key_file = key_file
        self._cipher = None
    
    @property
    def cipher(self):
        """获取或创建加密器"""
        if self._cipher is None:
            key = self._load_or_create_key()
            self._cipher = Fernet(key)
        return self._cipher
    
    def _load_or_create_key(self) -> bytes:
        """加载或创建主密钥"""
        os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
        
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)  # 只有所有者可读写
            return key
    
    def encrypt_api_key(self, key: str) -> str:
        """加密 API 密钥"""
        return self.cipher.encrypt(key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密 API 密钥"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()

# Provider 工厂
class ProviderFactory:
    """Provider 工厂类"""
    
    _providers = {
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
        # 可以继续添加其他 provider
    }
    
    @classmethod
    def create(cls, config: ProviderConfig) -> LLMProviderInterface:
        """创建 Provider 实例"""
        provider_class = cls._providers.get(config.name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.name}")
        
        return provider_class(config)
    
    @classmethod
    def register(cls, name: str, provider_class: type):
        """注册新的 Provider"""
        cls._providers[name.lower()] = provider_class

# Provider 管理器（带连接池）
class ProviderManager:
    """Provider 管理器，支持连接池和负载均衡"""
    
    def __init__(self, max_connections: int = 5):
        self._providers: Dict[str, List[LLMProviderInterface]] = {}
        self._max_connections = max_connections
        self._lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def get_provider(self, config: ProviderConfig) -> LLMProviderInterface:
        """获取 Provider 实例"""
        key = f"{config.name}:{config.model}"
        
        async with self._lock:
            if key not in self._providers:
                self._providers[key] = []
            
            # 从池中获取可用的 provider
            for provider in self._providers[key]:
                if await provider.health_check():
                    return provider
            
            # 创建新的 provider
            if len(self._providers[key]) < self._max_connections:
                provider = ProviderFactory.create(config)
                self._providers[key].append(provider)
                return provider
            
            # 池已满，等待并重试
            await asyncio.sleep(0.1)
            return await self.get_provider(config)
    
    async def cleanup(self):
        """清理资源"""
        # 实现清理逻辑
        pass

# 使用示例
async def main():
    # 配置
    config = ProviderConfig(
        name="ollama",
        model="deepseek-r1:14b",
        server_address="127.0.0.1:11434",
        is_local=True
    )
    
    # 创建 provider
    provider = ProviderFactory.create(config)
    
    # 生成文本
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    try:
        response = await provider.generate(messages)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())