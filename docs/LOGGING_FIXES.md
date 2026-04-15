# 日志系统修复说明

## 修复的问题

### 1. 日志重复打印问题

**问题描述：**
每个日志消息会被打印三次，这是因为子日志器添加了重复的handlers并传播到父日志器。

**解决方案：**
修改了 `src/core/logger.py` 中的 `_setup_child_loggers` 和 `_create_logger` 方法：

1. 子日志器不再添加自己的handler
2. 子日志器设置为传播到父日志器（`propagate = True`）
3. 只有根日志器（'agent'）添加控制台和文件handler

**代码变更：**
```python
def _setup_child_loggers(self, parent_name: str, level: str):
    """设置子模块日志器"""
    child_modules = ['loop', 'tools', 'cli']
    for module in child_modules:
        logger = logging.getLogger(f'{parent_name}.{module}')
        logger.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))
        # 让子logger传播到父logger，不添加自己的handler
        logger.propagate = True

def _create_logger(self, name: str) -> logging.Logger:
    """创建新日志器"""
    logger = logging.getLogger(name)
    # 不添加handler，只让传播到父logger
    # 如果是子logger（包含点），设置为传播但不添加自己的handler
    if '.' in name:
        logger.propagate = True
        # 确保没有重复的handler
        if logger.handlers:
            logger.handlers.clear()
    else:
        # 根logger如果没有handler，添加一个基本的控制台处理器
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                ColoredFormatter(
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

    self._loggers[name] = logger
    return logger
```

### 2. UnicodeDecodeError 问题

**问题描述：**
在Windows系统上执行 `dir /S /B resources` 等命令时，出现以下错误：
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0xaa in position 115: illegal multibyte sequence
```

**解决方案：**
修改了 `src/tools/bash.py` 中的 `bash` 函数，添加了字符编码错误处理：

```python
try:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
        encoding='utf-8',
        errors='replace'  # 替换无法解码的字符而不是抛出异常
    )
    # ... 其他代码
```

**关键参数：**
- `encoding='utf-8'`: 明确指定UTF-8编码
- `errors='replace'`: 遇到无法解码的字符时，用替换字符（�）代替抛出异常

## 测试验证

修复后进行以下测试：

### 日志重复测试
- ✅ 主日志器消息只输出一次
- ✅ 子日志器（如agent.tools.bash）消息只输出一次
- ✅ 日志传播正常工作

### Unicode处理测试
- ✅ 执行包含特殊字符的Windows命令不报错
- ✅ 中文目录和文件名正常处理
- ✅ 命令执行结果正确返回

## 使用建议

### 日志器使用
```python
from src.core.logger import get_logger

# 获取模块日志器
logger = get_logger('agent.tools.my_module')

# 记录消息（现在只会输出一次）
logger.info("This message will only appear once")
```

### Bash工具使用
```python
from src.tools.bash import bash

# 执行命令（现在可以处理包含特殊字符的输出）
result = bash("dir /S /B resources")
if result['success']:
    print(result['output'])  # 输出可能包含替换字符
else:
    print(f"Error: {result['error']}")
```

## 性能影响

修复后的日志系统具有以下性能特点：

1. **内存使用优化**：子日志器不创建重复handlers
2. **执行效率提升**：减少了重复日志的处理开销
3. **稳定性增强**：Unicode错误不会中断程序执行

## 升级说明

如果从旧版本升级：

1. 重新部署 `src/core/logger.py`
2. 重新部署 `src/tools/bash.py`
3. 清除现有的 `logs/` 目录中的旧日志文件（可选）
4. 重启Agent以应用新的日志配置

## 已知限制

1. **字符替换**：无法解码的字符会被替换为 � 符号
2. **编码假设**：默认使用UTF-8编码，某些Windows系统可能需要其他编码

如果遇到编码问题，可以在 `.env` 文件中设置合适的编码，或者修改 `src/tools/bash.py` 中的编码设置。

## 监控建议

建议监控以下指标：

1. **日志文件大小**：确保日志轮转正常工作
2. **日志重复检查**：确认没有重复日志消息
3. **错误率**：监控Unicode错误的频率
4. **性能影响**：观察日志对性能的影响
