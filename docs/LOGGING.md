# Agent 日志系统使用指南

## 概述

本项目使用了标准的 Python logging 框架，提供了结构化、可配置的日志系统。日志系统支持：

- 彩色控制台输出
- 文件日志存储
- 多级别日志记录（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 模块化日志器
- 自动日志轮转（按日期）

## 日志配置

### 初始化

日志系统在 `src/cli/main.py` 中自动初始化：

```python
from src.core.logger import initialize_logging

logger = initialize_logging(
    name='agent',              # 日志器名称
    level='INFO',              # 日志级别
    log_dir='logs',            # 日志目录
    enable_console=True,        # 启用控制台输出
    enable_file=True            # 启用文件输出
)
```

### 环境变量配置

可以通过 `.env` 文件配置日志级别：

```
LOG_LEVEL=DEBUG
```

支持的日志级别：
- `DEBUG` - 详细的调试信息
- `INFO` - 一般信息（默认）
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

## 在代码中使用日志

### 导入日志器

```python
from src.core.logger import get_logger

# 获取模块特定的日志器
logger = get_logger('agent.your_module')
```

### 日志级别

```python
logger.debug("调试信息")      # 详细的调试信息
logger.info("一般信息")       # 一般信息
logger.warning("警告信息")    # 警告信息
logger.error("错误信息")      # 错误信息
logger.critical("严重错误")   # 严重错误
```

### 异常日志

记录异常时包含堆栈跟踪：

```python
try:
    # 一些操作
    pass
except Exception as e:
    logger.error(f"操作失败: {str(e)}", exc_info=True)
```

## 日志器命名规范

为了更好的日志组织和过滤，建议按照模块层次结构命名日志器：

- `agent` - 主Agent模块
- `agent.loop` - 循环模块
- `agent.tools` - 工具模块
- `agent.tools.bash` - bash工具
- `agent.tools.file` - 文件工具
- `agent.tools.todo` - todo工具
- `agent.tools.sub_agent` - sub_agent工具

示例：

```python
logger = get_logger('agent.tools.my_new_tool')
```

## 日志文件

日志文件存储在 `logs/` 目录下，按日期命名：

```
logs/
├── agent_20260415.log
├── agent_20260416.log
└── ...
```

日志文件格式：
```
2026-04-15 10:30:45 - agent.tools.bash - INFO - Executing command: ls
2026-04-15 10:30:46 - agent.tools.bash - INFO - Command completed with return code: 0
```

## 控制台输出

控制台日志使用彩色格式，便于快速识别问题：

- 🟦 DEBUG - 青色
- 🟩 INFO - 绿色
- 🟨 WARNING - 黄色
- 🟥 ERROR - 红色
- 🟪 CRITICAL - 紫色

## 最佳实践

### 1. 使用适当的日志级别

- `DEBUG`: 详细的调试信息，只在开发时使用
- `INFO`: 重要的操作和状态变化
- `WARNING`: 潜在问题，但程序可以继续
- `ERROR`: 错误，影响当前操作
- `CRITICAL`: 严重错误，程序可能需要退出

### 2. 包含上下文信息

```python
# 不好
logger.error("文件读取失败")

# 好
logger.error(f"文件读取失败: {file_path}, 原因: {str(e)}")
```

### 3. 避免敏感信息

```python
# 不要记录敏感信息
logger.info(f"API Key: {api_key}")  # ❌ 错误

# 记录脱敏信息
logger.info(f"使用API Key: {api_key[:8]}...")  # ✅ 正确
```

### 4. 性能考虑

```python
# 在DEBUG级别时，避免昂贵的字符串格式化
logger.debug(f"处理数据: {json.dumps(large_data, indent=2)}")  # ❌ 每次都格式化

# 使用懒惰求值
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"处理数据: {json.dumps(large_data, indent=2)}")  # ✅ 仅在需要时格式化
```

## 故障排除

### 日志不显示

1. 检查日志级别设置是否正确
2. 确认日志器已正确初始化
3. 验证日志器名称是否正确

### 日志文件未创建

1. 检查 `logs/` 目录权限
2. 确认 `enable_file=True` 在初始化时设置
3. 检查磁盘空间

### 性能问题

1. 降低日志级别（INFO -> WARNING）
2. 禁用文件日志（`enable_file=False`）
3. 避免在循环中记录DEBUG级别日志
