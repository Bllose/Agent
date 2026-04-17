"""
消息序列化助手类

处理 Agent messages 对象的序列化，处理包含 ToolUseBlock 等不可序列化对象的情况。
"""
import copy
from typing import Any, List, Dict, Optional, Union


class MessageHelper:
    """消息序列化助手类"""

    def __init__(self, max_value_length: Optional[int] = None):
        """
        初始化消息助手

        Args:
            max_value_length: 当值超过此长度时进行截断显示，None 表示不截断
        """
        self.max_value_length = max_value_length

    def serialize(self, messages: List[Any], index: Optional[int] = None,
                  truncate_keys: Optional[List[str]] = None) -> Union[List[Any], Dict[str, Any], Any]:
        """
        序列化 messages 对象

        Args:
            messages: 消息列表
            index: 指定要序列化的消息索引，None 表示序列化全部
            truncate_keys: 需要截断显示的 key 列表，None 表示不截断

        Returns:
            序列化后的消息对象
        """
        if index is not None:
            # 单独序列化指定索引的元素
            if 0 <= index < len(messages):
                return self._serialize_message(messages[index], truncate_keys)
            else:
                raise IndexError(f"Index {index} out of range for messages list of length {len(messages)}")
        else:
            # 序列化全部消息
            serialized = []
            for msg in messages:
                serialized.append(self._serialize_message(msg, truncate_keys))
            return serialized

    def _serialize_message(self, message: Any, truncate_keys: Optional[List[str]] = None) -> Any:
        """
        序列化单个消息对象

        Args:
            message: 消息对象
            truncate_keys: 需要截断显示的 key 列表

        Returns:
            序列化后的消息
        """
        if isinstance(message, dict):
            serialized_msg = {}
            for key, value in message.items():
                if key == 'content':
                    # 处理 content 可能是 TextBlock 或 ToolUseBlock 对象
                    serialized_content = self._serialize_content(value, truncate_keys)

                    # 检查 content 字段是否需要截断
                    if truncate_keys and key in truncate_keys:
                        # 将序列化后的 content 转换为字符串进行截断
                        content_str = str(serialized_content)
                        serialized_msg[key] = self._truncate_value(content_str)
                    else:
                        serialized_msg[key] = serialized_content
                else:
                    # 处理其他字段，检查是否需要截断
                    if truncate_keys and key in truncate_keys:
                        serialized_msg[key] = self._truncate_value(value)
                    else:
                        serialized_msg[key] = self._try_serialize_value(value)
            return serialized_msg
        else:
            # 非字典类型消息
            return self._try_serialize_value(message)

    def _serialize_content(self, content: Any, truncate_keys: Optional[List[str]] = None) -> Any:
        """
        序列化 content 字段

        Args:
            content: content 内容
            truncate_keys: 需要截断显示的 key 列表

        Returns:
            序列化后的 content
        """
        # 检查是否为 block 对象列表（如 TextBlock, ToolUseBlock）
        if hasattr(content, '__iter__') and not isinstance(content, (str, bytes)):
            try:
                content_list = []
                for block in content:
                    if hasattr(block, '__dict__'):
                        # 处理 block 对象（如 ToolUseBlock, TextBlock）
                        serialized_block = self._serialize_block(block, truncate_keys)
                        content_list.append(serialized_block)
                    else:
                        content_list.append(str(block))
                return content_list
            except TypeError:
                # 如果不是可迭代对象，直接尝试序列化
                return self._try_serialize_value(content)
        else:
            # 字符串或其他简单类型
            return content

    def _serialize_block(self, block: Any, truncate_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        序列化 block 对象（如 ToolUseBlock, TextBlock）

        Args:
            block: block 对象
            truncate_keys: 需要截断显示的 key 列表

        Returns:
            序列化后的 block 字典
        """
        serialized = {}

        # 获取 block 的所有属性
        if hasattr(block, '__dict__'):
            for attr_name, attr_value in block.__dict__.items():
                if attr_name.startswith('_'):
                    continue  # 跳过私有属性

                # 检查是否需要截断
                if truncate_keys and attr_name in truncate_keys:
                    serialized[attr_name] = self._truncate_value(attr_value)
                else:
                    serialized[attr_name] = self._try_serialize_value(attr_value)

        # 同时也尝试获取常见属性（以防 __dict__ 中没有）
        common_attrs = ['type', 'text', 'input', 'id', 'name', 'content', 'model']
        for attr in common_attrs:
            if hasattr(block, attr) and attr not in serialized:
                value = getattr(block, attr)
                if truncate_keys and attr in truncate_keys:
                    serialized[attr] = self._truncate_value(value)
                else:
                    serialized[attr] = self._try_serialize_value(value)

        return serialized

    def _try_serialize_value(self, value: Any) -> Any:
        """
        尝试序列化值，处理各种数据类型

        Args:
            value: 要序列化的值

        Returns:
            可序列化的值
        """
        # 基本类型直接返回
        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        # 列表类型
        if isinstance(value, list):
            return [self._try_serialize_value(item) for item in value]

        # 字典类型
        if isinstance(value, dict):
            return {k: self._try_serialize_value(v) for k, v in value.items()}

        # 其他类型尝试转换为字符串
        return str(value)

    def _truncate_value(self, value: Any, prefix_length: int = 200, suffix_length: int = 200) -> Dict[str, Any]:
        """
        截断过长的值，显示部分内容和总长度

        Args:
            value: 要截断的值
            prefix_length: 前缀长度
            suffix_length: 后缀长度

        Returns:
            包含截断信息的字典
        """
        # 将值转换为字符串
        value_str = str(value)
        total_length = len(value_str)

        if self.max_value_length and total_length > self.max_value_length:
            # 如果启用了最大长度限制且超过限制
            truncated = True
            prefix = value_str[:prefix_length]
            suffix = value_str[-suffix_length:] if total_length > suffix_length else ""

            result = {
                '_truncated': True,
                '_total_length': total_length,
                '_display_length': prefix_length + suffix_length,
                'content': f"{prefix}...{suffix}" if suffix else f"{prefix}..."
            }
        elif total_length > prefix_length + suffix_length:
            # 值过长但未超过配置的最大长度限制
            truncated = True
            prefix = value_str[:prefix_length]
            suffix = value_str[-suffix_length:]

            result = {
                '_truncated': True,
                '_total_length': total_length,
                '_display_length': prefix_length + suffix_length,
                'content': f"{prefix}...{suffix}"
            }
        else:
            # 值不需要截断
            truncated = False
            result = {
                '_truncated': False,
                '_total_length': total_length,
                'content': value_str
            }

        return result

    def get_message_info(self, messages: List[Any]) -> Dict[str, Any]:
        """
        获取 messages 的基本信息（不进行完整序列化）

        Args:
            messages: 消息列表

        Returns:
            包含消息列表信息的字典
        """
        info = {
            'total_count': len(messages),
            'message_types': {},
            'total_estimated_length': 0
        }

        for msg in messages:
            msg_type = type(msg).__name__
            info['message_types'][msg_type] = info['message_types'].get(msg_type, 0) + 1

            # 估算长度（粗略）
            if isinstance(msg, dict):
                info['total_estimated_length'] += len(str(msg))
            else:
                info['total_estimated_length'] += len(str(msg))

        return info


# 便捷函数
def serialize_messages(messages: List[Any], index: Optional[int] = None,
                       max_value_length: Optional[int] = None,
                       truncate_keys: Optional[List[str]] = None) -> Union[List[Any], Dict[str, Any], Any]:
    """
    便捷函数：序列化消息列表

    Args:
        messages: 消息列表
        index: 指定要序列化的消息索引
        max_value_length: 最大值长度限制
        truncate_keys: 需要截断显示的 key 列表

    Returns:
        序列化后的消息
    """
    helper = MessageHelper(max_value_length=max_value_length)
    return helper.serialize(messages, index=index, truncate_keys=truncate_keys)
