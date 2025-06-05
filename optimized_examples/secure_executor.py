"""
安全的命令执行器
包含输入验证、命令白名单、路径检查和执行隔离
"""
import os
import subprocess
import asyncio
import tempfile
import shlex
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import logging
from datetime import datetime

class CommandStatus(Enum):
    """命令执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"

@dataclass
class CommandResult:
    """命令执行结果"""
    command: str
    status: CommandStatus
    stdout: str
    stderr: str
    exit_code: Optional[int]
    execution_time: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "command": self.command,
            "status": self.status.value,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat()
        }

class SecurityValidator:
    """安全验证器"""
    
    # 默认允许的命令
    DEFAULT_ALLOWED_COMMANDS = {
        "python", "python3", "pip", "pip3",
        "node", "npm", "yarn",
        "go", "cargo", "rustc",
        "java", "javac", "mvn", "gradle",
        "gcc", "g++", "make", "cmake",
        "git", "curl", "wget",
        "ls", "cat", "echo", "grep", "find", "head", "tail",
        "mkdir", "touch", "cp", "mv", "rm"
    }
    
    # 危险的命令模式
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",  # 删除根目录
        r":(){ :|:& };:",  # Fork bomb
        r">\s*/dev/s[a-z]+",  # 写入设备
        r"dd\s+if=/dev/zero",  # 覆盖磁盘
        r"mkfs\.",  # 格式化文件系统
        r"chmod\s+777\s+/",  # 修改根目录权限
        r"eval\s*\(",  # 动态执行代码
        r"exec\s*\(",  # 动态执行代码
    ]
    
    # 环境变量黑名单
    FORBIDDEN_ENV_VARS = {
        "LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH",
        "PATH", "HOME", "USER", "SHELL"
    }
    
    def __init__(self, 
                 allowed_commands: Optional[List[str]] = None,
                 forbidden_paths: Optional[List[Path]] = None,
                 max_command_length: int = 1000):
        self.allowed_commands = set(allowed_commands or self.DEFAULT_ALLOWED_COMMANDS)
        self.forbidden_paths = forbidden_paths or [
            Path("/etc"),
            Path("/sys"),
            Path("/proc"),
            Path("/boot"),
            Path("/dev"),
            Path("/root")
        ]
        self.max_command_length = max_command_length
        self.logger = logging.getLogger(__name__)
    
    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """验证命令是否安全"""
        # 长度检查
        if len(command) > self.max_command_length:
            return False, f"Command too long (max {self.max_command_length} chars)"
        
        # 解析命令
        try:
            args = shlex.split(command)
            if not args:
                return False, "Empty command"
            
            base_command = os.path.basename(args[0])
        except Exception as e:
            return False, f"Invalid command format: {e}"
        
        # 命令白名单检查
        if base_command not in self.allowed_commands:
            return False, f"Command '{base_command}' not in whitelist"
        
        # 危险模式检查
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # 路径检查
        for arg in args[1:]:
            if arg.startswith("/") or arg.startswith("~"):
                path = Path(arg).expanduser().resolve()
                for forbidden in self.forbidden_paths:
                    try:
                        path.relative_to(forbidden)
                        return False, f"Access to {forbidden} is forbidden"
                    except ValueError:
                        pass
        
        # 环境变量注入检查
        for var in self.FORBIDDEN_ENV_VARS:
            if f"${var}" in command or f"${{{var}}}" in command:
                return False, f"Environment variable {var} is forbidden"
        
        return True, None
    
    def sanitize_path(self, path: str, base_dir: Path) -> Optional[Path]:
        """清理和验证路径"""
        try:
            # 解析路径
            clean_path = Path(path).expanduser().resolve()
            
            # 确保路径在基础目录内
            clean_path.relative_to(base_dir)
            
            # 检查是否访问禁止的路径
            for forbidden in self.forbidden_paths:
                try:
                    clean_path.relative_to(forbidden)
                    return None
                except ValueError:
                    pass
            
            return clean_path
        except Exception:
            return None

class SecureExecutor:
    """安全的命令执行器"""
    
    def __init__(self,
                 work_dir: Path,
                 validator: Optional[SecurityValidator] = None,
                 timeout: int = 30,
                 max_output_size: int = 1024 * 1024):  # 1MB
        self.work_dir = Path(work_dir).resolve()
        self.validator = validator or SecurityValidator()
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.logger = logging.getLogger(__name__)
        
        # 创建工作目录
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 执行历史
        self.history: List[CommandResult] = []
    
    async def execute(self, command: str, cwd: Optional[Path] = None) -> CommandResult:
        """安全执行命令"""
        start_time = datetime.now()
        
        # 验证命令
        is_valid, error = self.validator.validate_command(command)
        if not is_valid:
            self.logger.warning(f"Command blocked: {command} - {error}")
            result = CommandResult(
                command=command,
                status=CommandStatus.BLOCKED,
                stdout="",
                stderr=error or "Command blocked by security policy",
                exit_code=None,
                execution_time=0,
                timestamp=start_time
            )
            self.history.append(result)
            return result
        
        # 设置工作目录
        if cwd:
            cwd = self.validator.sanitize_path(str(cwd), self.work_dir)
            if not cwd:
                result = CommandResult(
                    command=command,
                    status=CommandStatus.BLOCKED,
                    stdout="",
                    stderr="Invalid working directory",
                    exit_code=None,
                    execution_time=0,
                    timestamp=start_time
                )
                self.history.append(result)
                return result
        else:
            cwd = self.work_dir
        
        # 创建隔离的环境变量
        env = self._create_safe_env()
        
        # 执行命令
        try:
            # 解析命令
            args = shlex.split(command)
            
            # 创建进程
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
                # 限制资源使用
                preexec_fn=self._limit_resources if os.name != 'nt' else None
            )
            
            # 等待执行完成
            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                # 限制输出大小
                stdout = self._truncate_output(stdout_data.decode('utf-8', errors='replace'))
                stderr = self._truncate_output(stderr_data.decode('utf-8', errors='replace'))
                
                status = CommandStatus.SUCCESS if process.returncode == 0 else CommandStatus.FAILED
                
            except asyncio.TimeoutError:
                # 超时处理
                process.kill()
                await process.wait()
                stdout = ""
                stderr = f"Command timed out after {self.timeout} seconds"
                status = CommandStatus.TIMEOUT
            
            result = CommandResult(
                command=command,
                status=status,
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode,
                execution_time=(datetime.now() - start_time).total_seconds(),
                timestamp=start_time
            )
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            result = CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                stdout="",
                stderr=str(e),
                exit_code=None,
                execution_time=(datetime.now() - start_time).total_seconds(),
                timestamp=start_time
            )
        
        self.history.append(result)
        return result
    
    def _create_safe_env(self) -> Dict[str, str]:
        """创建安全的环境变量"""
        # 只保留必要的环境变量
        safe_env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
            "HOME": str(self.work_dir),
            "TMPDIR": str(self.work_dir / "tmp"),
            "USER": "sandbox",
            "LOGNAME": "sandbox",
        }
        
        # 创建临时目录
        tmp_dir = self.work_dir / "tmp"
        tmp_dir.mkdir(exist_ok=True)
        
        return safe_env
    
    def _limit_resources(self):
        """限制进程资源（仅 Unix）"""
        import resource
        
        # CPU 时间限制（秒）
        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
        
        # 内存限制（字节）
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        
        # 文件大小限制（字节）
        resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
        
        # 进程数限制
        resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
    
    def _truncate_output(self, output: str) -> str:
        """截断过长的输出"""
        if len(output) > self.max_output_size:
            return output[:self.max_output_size] + f"\n... (truncated, total {len(output)} bytes)"
        return output
    
    async def execute_script(self, script_content: str, language: str = "python") -> CommandResult:
        """安全执行脚本"""
        # 支持的语言和扩展名
        language_map = {
            "python": (".py", ["python3", "-u"]),
            "javascript": (".js", ["node"]),
            "go": (".go", ["go", "run"]),
            "java": (".java", ["java"]),
            "bash": (".sh", ["bash"]),
            "ruby": (".rb", ["ruby"]),
        }
        
        if language not in language_map:
            return CommandResult(
                command=f"execute_{language}_script",
                status=CommandStatus.FAILED,
                stdout="",
                stderr=f"Unsupported language: {language}",
                exit_code=None,
                execution_time=0,
                timestamp=datetime.now()
            )
        
        ext, cmd_prefix = language_map[language]
        
        # 创建临时脚本文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=ext,
            dir=self.work_dir / "tmp",
            delete=False
        ) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            # 构建命令
            command = " ".join(cmd_prefix + [script_path])
            
            # 执行脚本
            result = await self.execute(command)
            
            # 添加脚本内容的哈希到结果中
            result.command = f"{command} (script hash: {hashlib.md5(script_content.encode()).hexdigest()[:8]})"
            
            return result
            
        finally:
            # 清理临时文件
            try:
                os.unlink(script_path)
            except Exception:
                pass
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return [result.to_dict() for result in self.history[-limit:]]
    
    def save_history(self, file_path: Path):
        """保存执行历史"""
        history_data = {
            "work_dir": str(self.work_dir),
            "commands": [result.to_dict() for result in self.history]
        }
        
        with open(file_path, 'w') as f:
            json.dump(history_data, f, indent=2)

# 使用示例
async def main():
    # 创建安全执行器
    executor = SecureExecutor(
        work_dir=Path("./sandbox"),
        timeout=10
    )
    
    # 测试命令执行
    commands = [
        "echo 'Hello, World!'",
        "python3 --version",
        "ls -la",
        "rm -rf /",  # 这个会被阻止
        "cat /etc/passwd",  # 这个会被阻止
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        result = await executor.execute(cmd)
        print(f"Status: {result.status.value}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    
    # 测试脚本执行
    python_script = """
import sys
print("Python version:", sys.version)
print("Hello from secure executor!")
"""
    
    print("\nExecuting Python script:")
    result = await executor.execute_script(python_script, "python")
    print(f"Status: {result.status.value}")
    print(f"Output: {result.stdout}")
    
    # 保存历史
    executor.save_history(Path("execution_history.json"))

if __name__ == "__main__":
    asyncio.run(main())