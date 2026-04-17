# MessageHelper 消息序列化助手

## 概述

`MessageHelper` 是用于序列化 Agent `messages` 对象的工具类，专门处理包含 `ToolUseBlock`、`TextBlock` 等 Anthropic SDK 对象的序列化问题。

## 核心功能

### 1. 基本序列化
自动处理各种数据类型和 Anthropic SDK 对象：
- 字典、列表、基本类型
- `ToolUseBlock` 对象
- `TextBlock` 对象
- 其他自定义对象

###.2. 按索引序列化
可以单独序列化 messages 列表中指定索引的元素，便于调试和查看特定消息。

### 3. 值截断
当指定字段的值过长时，自动截断显示部分内容，并记录总长度信息。

### 4. 消息统计
快速获取 messages 列表的统计信息，包括数量、类型分布、估算长度等。

## 使用方法

### 基本用法

```python
from src.helper import MessageHelper

# 初始化
helper = MessageHelper()

# 序列化全部消息
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there"}
]
serialized = helper.serialize(messages)
```

### 按索引序列化

```python
# 只序列化索引 1 的消息
single_msg = helper.serialize(messages, index=1)
```

### 值截断

```python
# 配置最大长度为 500 字符
helper = MessageHelper(max_value_length=500)

# 指定要对 'content' 字段进行截断
serialized = helper.serialize(messages, truncate_keys=['content'])

# 截断后的格式
# {
#     '_truncated': True,
#     '_total_length': 10000,
#     '_display_length': 400,
#     'content': '前200字符...后200字符'
# }
```

### 获取消息统计信息

```python
info = helper.get_message_info(messages)

# {
#     'total_count': 5,
#     'message_types': {'dict': 5},
#     'total_estimated_length': 1234
# }
```

### 在 Agent 中使用

```python
import json
from src.helper import serialize_messages

class Agent:
    def save_state(self):
        # 序列化 messages 以便保存到磁盘
        serialized = serialize_messages(self.messages)

        # 可以安全地 JSON 序列化
        json_data = json.dumps(serialized, ensure_ascii=False)
        return json_data
```

## 便捷函数

```python
from src.helper import serialize_messages

# 一行代码完成序列化
result = serialize_messages(messages, index=1, max_value_length=500)
```

## 测试

运行测试：
```bash
python src/helper/test_message_helper.py
```

运行使用示例：
```bash
python src/helper/example.py
```

## 在 VSCode DEBUG CONSOLE 中使用

当你在 VSCode 中调试 Agent 时，可以方便地查看 messages：

### 方式 1: 直接导入

在 DEBUG CONSOLE 中输入：

```python
from src.helper import serialize_messages, MessageHelper
helper = MessageHelper(max_value_length=500)

# 查看所有消息（自动截断过长的 content）
serialize_messages(messages, truncate_keys=['content'])

# 查看指定索引的消息
helper.serialize(messages, index=0, truncate_keys=['content'])

# 获取消息统计
helper.get_message_info(messages)
```

### 方式 2: 使用快捷命令

在 DEBUG CONSOLE 中复制以下代码定义快捷函数：

```python
def dbg(msgs=None, index=None):
    from src.helper import MessageHelper
    if msgs is None:
        try:
            msgs = self.messages
        except NameError:
            return "错误：未找到 messages 变量"
    helper = MessageHelper(max_value_length=500)
    if index is not None:
        return helper.serialize(msgs, index=index, truncate_keys=['content'])
    return helper.serialize(msgs, truncate_keys=['content'])
```

然后使用快捷命令：

```python
dbg()               # 查看所有 messages
dbg(messages)       # 查看所有 messages（显式传入）
dbg(messages, 0)   # 查看索引 0 的消息
```

### 在 Agent 类中调试

```python
# 查看 agent.messages
from src.helper import serialize_messages
serialize_messages(agent.messages, truncate_keys=['content'])

# 或者使用快捷命令
def dbg_agent(agent, index=None):
    from src.helper import MessageHelper
    helper = MessageHelper(max_value_length=500)
    if index is not None:
        return helper.serialize(agent.messages, index=index, truncate_keys=['content'])
    return helper.serialize(agent.messages, truncate_keys=['content'])

dbg_agent(agent)      # 查看所有消息
dbg_agent(agent, -1)  # 查看最后一条消息
```

### 在 loop.py 中调试

```python
# 查看 self.agent.messages
from src.helper import serialize_messages
serialize_messages(self.agent.messages, truncate_keys=['content'])
```

## 文件结构

```
src/helper/
├── __init__.py           # 导出接口
├── message_helper.py      # 主实现
├── test_message_helper.py # 单元测试
├── example.py            # 使用示例
└── README.md             # 说明文档
```
