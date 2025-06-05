"""
优化后的配置管理系统
使用 Pydantic 进行类型验证和环境变量管理
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator, SecretStr
from pydantic.networks import HttpUrl
from pathlib import Path
import os
from enum import Enum

class ProviderType(str, Enum):
    """支持的 Provider 类型"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    LM_STUDIO = "lm-studio"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    TOGETHER = "together"
    SERVER = "server"

class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class BrowserSettings(BaseSettings):
    """浏览器相关配置"""
    headless: bool = Field(True, description="是否使用无头浏览器")
    stealth_mode: bool = Field(True, description="是否使用隐身模式")
    user_agent: Optional[str] = Field(None, description="自定义 User Agent")
    window_size: tuple = Field((1920, 1080), description="浏览器窗口大小")
    download_dir: Path = Field(Path("./downloads"), description="下载目录")
    screenshot_dir: Path = Field(Path("./.screenshots"), description="截图目录")
    timeout: int = Field(30, description="页面加载超时时间（秒）")
    
    @validator("download_dir", "screenshot_dir", pre=True)
    def create_directories(cls, v):
        """自动创建目录"""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

class ProviderSettings(BaseSettings):
    """LLM Provider 配置"""
    name: ProviderType = Field(ProviderType.OLLAMA, description="Provider 名称")
    model: str = Field("deepseek-r1:14b", description="模型名称")
    server_address: str = Field("127.0.0.1:11434", description="服务器地址")
    is_local: bool = Field(True, description="是否本地运行")
    timeout: int = Field(60, description="请求超时时间（秒）")
    max_retries: int = Field(3, description="最大重试次数")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="生成温度")
    max_tokens: Optional[int] = Field(None, description="最大 token 数")
    
    # API 密钥（使用 SecretStr 保护）
    openai_api_key: Optional[SecretStr] = Field(None, env="OPENAI_API_KEY")
    google_api_key: Optional[SecretStr] = Field(None, env="GOOGLE_API_KEY")
    deepseek_api_key: Optional[SecretStr] = Field(None, env="DEEPSEEK_API_KEY")
    together_api_key: Optional[SecretStr] = Field(None, env="TOGETHER_API_KEY")
    
    @validator("server_address")
    def validate_server_address(cls, v, values):
        """验证服务器地址格式"""
        if values.get("is_local") and not v.startswith(("127.0.0.1", "localhost", "http://", "https://")):
            # 对于本地服务，确保地址格式正确
            if ":" not in v:
                raise ValueError("Server address must include port (e.g., '127.0.0.1:11434')")
        return v
    
    def get_api_key(self) -> Optional[str]:
        """获取当前 provider 的 API 密钥"""
        key_map = {
            ProviderType.OPENAI: self.openai_api_key,
            ProviderType.GOOGLE: self.google_api_key,
            ProviderType.DEEPSEEK: self.deepseek_api_key,
            ProviderType.TOGETHER: self.together_api_key,
        }
        
        key = key_map.get(self.name)
        return key.get_secret_value() if key else None

class AgentSettings(BaseSettings):
    """Agent 相关配置"""
    name: str = Field("Jarvis", description="AI 助手名称")
    personality: str = Field("base", description="个性化配置文件夹")
    recover_last_session: bool = Field(True, description="是否恢复上次会话")
    save_session: bool = Field(True, description="是否保存会话")
    work_dir: Path = Field(Path.home() / "Documents" / "ai_workspace", description="工作目录")
    session_dir: Path = Field(Path("./.sessions"), description="会话存储目录")
    max_session_size: int = Field(100, description="最大会话消息数")
    
    @validator("work_dir", "session_dir", pre=True)
    def expand_path(cls, v):
        """展开路径"""
        path = Path(v).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

class AudioSettings(BaseSettings):
    """音频相关配置"""
    speak: bool = Field(False, description="是否启用文本转语音")
    listen: bool = Field(False, description="是否启用语音识别")
    languages: List[str] = Field(["en", "zh"], description="支持的语言列表")
    voice_model: str = Field("kokoro", description="TTS 模型")
    wake_word: Optional[str] = Field(None, description="唤醒词")
    audio_device_index: Optional[int] = Field(None, description="音频设备索引")
    
    @validator("languages")
    def validate_languages(cls, v):
        """验证语言代码"""
        supported = {"en", "zh", "fr", "ja", "pt", "es", "de", "ru"}
        for lang in v:
            if lang not in supported:
                raise ValueError(f"Unsupported language: {lang}")
        return v

class SecuritySettings(BaseSettings):
    """安全相关配置"""
    enable_command_validation: bool = Field(True, description="是否验证命令执行")
    allowed_commands: List[str] = Field(
        ["python", "node", "go", "java", "gcc", "ls", "cat", "echo"],
        description="允许执行的命令白名单"
    )
    forbidden_paths: List[Path] = Field(
        [Path("/etc"), Path("/sys"), Path("/proc")],
        description="禁止访问的路径"
    )
    max_file_size: int = Field(10 * 1024 * 1024, description="最大文件大小（字节）")
    enable_api_auth: bool = Field(False, description="是否启用 API 认证")
    api_token: Optional[SecretStr] = Field(None, env="AGENTIC_API_TOKEN")

class LoggingSettings(BaseSettings):
    """日志配置"""
    level: LogLevel = Field(LogLevel.INFO, description="日志级别")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    file: Optional[Path] = Field(Path("./logs/agenticseek.log"), description="日志文件路径")
    max_size: int = Field(10 * 1024 * 1024, description="日志文件最大大小")
    backup_count: int = Field(5, description="日志文件备份数量")
    
    @validator("file", pre=True)
    def create_log_dir(cls, v):
        """创建日志目录"""
        if v:
            path = Path(v)
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        return v

class Settings(BaseSettings):
    """主配置类"""
    # 子配置
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    provider: ProviderSettings = Field(default_factory=ProviderSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    # 服务配置
    api_host: str = Field("0.0.0.0", description="API 服务监听地址")
    api_port: int = Field(8000, description="API 服务端口")
    frontend_url: str = Field("http://localhost:3000", description="前端 URL")
    searxng_url: str = Field("http://localhost:8080", description="SearXNG URL")
    redis_url: str = Field("redis://localhost:6379/0", description="Redis URL")
    
    # 开发配置
    debug: bool = Field(False, description="调试模式")
    reload: bool = Field(False, description="自动重载")
    
    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "AGENTIC_"
        case_sensitive = False
        
        # 允许通过环境变量覆盖嵌套配置
        # 例如：AGENTIC_PROVIDER__MODEL=gpt-4
        env_nested_delimiter = "__"
    
    def to_ini(self, file_path: Path):
        """导出为 INI 格式（兼容旧版本）"""
        import configparser
        
        config = configparser.ConfigParser()
        
        # MAIN section
        config["MAIN"] = {
            "is_local": str(self.provider.is_local),
            "provider_name": self.provider.name,
            "provider_model": self.provider.model,
            "provider_server_address": self.provider.server_address,
            "agent_name": self.agent.name,
            "recover_last_session": str(self.agent.recover_last_session),
            "save_session": str(self.agent.save_session),
            "speak": str(self.audio.speak),
            "listen": str(self.audio.listen),
            "work_dir": str(self.agent.work_dir),
            "jarvis_personality": str(self.agent.personality == "jarvis"),
            "languages": " ".join(self.audio.languages),
        }
        
        # BROWSER section
        config["BROWSER"] = {
            "headless_browser": str(self.browser.headless),
            "stealth_mode": str(self.browser.stealth_mode),
        }
        
        with open(file_path, "w") as f:
            config.write(f)
    
    @classmethod
    def from_ini(cls, file_path: Path) -> "Settings":
        """从 INI 文件加载（兼容旧版本）"""
        import configparser
        
        config = configparser.ConfigParser()
        config.read(file_path)
        
        # 转换旧配置到新格式
        provider_settings = ProviderSettings(
            name=config.get("MAIN", "provider_name", fallback="ollama"),
            model=config.get("MAIN", "provider_model", fallback="deepseek-r1:14b"),
            server_address=config.get("MAIN", "provider_server_address", fallback="127.0.0.1:11434"),
            is_local=config.getboolean("MAIN", "is_local", fallback=True),
        )
        
        agent_settings = AgentSettings(
            name=config.get("MAIN", "agent_name", fallback="Jarvis"),
            personality="jarvis" if config.getboolean("MAIN", "jarvis_personality", fallback=False) else "base",
            recover_last_session=config.getboolean("MAIN", "recover_last_session", fallback=True),
            save_session=config.getboolean("MAIN", "save_session", fallback=True),
            work_dir=config.get("MAIN", "work_dir", fallback=str(Path.home() / "Documents" / "ai_workspace")),
        )
        
        audio_settings = AudioSettings(
            speak=config.getboolean("MAIN", "speak", fallback=False),
            listen=config.getboolean("MAIN", "listen", fallback=False),
            languages=config.get("MAIN", "languages", fallback="en zh").split(),
        )
        
        browser_settings = BrowserSettings(
            headless=config.getboolean("BROWSER", "headless_browser", fallback=True),
            stealth_mode=config.getboolean("BROWSER", "stealth_mode", fallback=True),
        )
        
        return cls(
            provider=provider_settings,
            agent=agent_settings,
            audio=audio_settings,
            browser=browser_settings,
        )

# 单例模式的配置实例
_settings_instance: Optional[Settings] = None

def get_settings() -> Settings:
    """获取配置单例"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

def reload_settings():
    """重新加载配置"""
    global _settings_instance
    _settings_instance = Settings()
    return _settings_instance

# 使用示例
if __name__ == "__main__":
    # 加载配置
    settings = get_settings()
    
    # 访问配置
    print(f"Provider: {settings.provider.name}")
    print(f"Model: {settings.provider.model}")
    print(f"Agent name: {settings.agent.name}")
    print(f"Work directory: {settings.agent.work_dir}")
    
    # 导出为 INI（兼容旧版本）
    settings.to_ini(Path("config_export.ini"))
    
    # 从 INI 加载
    loaded_settings = Settings.from_ini(Path("config.ini"))
    print(f"Loaded provider: {loaded_settings.provider.name}")