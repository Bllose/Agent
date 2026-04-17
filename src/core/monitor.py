"""
Agent 监控者模块
用于监控 Agent 的消息状态、token 消耗等统计信息
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TokenUsage:
    """Token 使用统计"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: 'TokenUsage') -> None:
        """累加 token 使用量"""
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.total_tokens += other.total_tokens


@dataclass
class ConversationStats:
    """单轮对话统计"""
    conversation_id: str
    started_at: datetime
    ended_at: datetime = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    message_count_start: int = 0
    message_count_end: int = 0
    message_count_added: int = 0


class AgentMonitor:
    """Agent 监控者类"""

    def __init__(self):
        """初始化监控者"""
        self.messages = None
        self.total_token_usage = TokenUsage()
        self.conversation_history = []
        self.current_conversation = None
        self.total_conversations = 0

    def set_messages_reference(self, messages: list):
        """
        设置对 Agent messages 的引用

        Args:
            messages: Agent 的消息列表对象
        """
        self.messages = messages

    def start_conversation(self, conversation_id: str):
        """
        开始一轮新的对话

        Args:
            conversation_id: 对话 ID
        """
        self.current_conversation = ConversationStats(
            conversation_id=conversation_id,
            started_at=datetime.now(),
            message_count_start=len(self.messages) if self.messages else 0
        )

    def record_token_usage(self, usage_dict: dict):
        """
        记录一次大模型调用的 token 使用情况

        Args:
            usage_dict: 大模型返回的 usage 字典，包含:
                - input_tokens: 输入 token 数
                - output_tokens: 输出 token 数
        """
        input_tokens = usage_dict.get('input_tokens', 0)
        output_tokens = usage_dict.get('output_tokens', 0)
        total_tokens = usage_dict.get('total_tokens', input_tokens + output_tokens)

        usage = TokenUsage(input_tokens, output_tokens, total_tokens)

        # 累加到当前对话
        if self.current_conversation:
            self.current_conversation.token_usage.add(usage)

        # 累加到总计
        self.total_token_usage.add(usage)

    def end_conversation(self):
        """结束当前对话并输出统计信息"""
        if not self.current_conversation:
            return

        self.current_conversation.ended_at = datetime.now()
        self.current_conversation.message_count_end = len(self.messages) if self.messages else 0
        self.current_conversation.message_count_added = (
            self.current_conversation.message_count_end -
            self.current_conversation.message_count_start
        )

        # 添加到历史记录
        self.conversation_history.append(self.current_conversation)
        self.total_conversations += 1

        # 输出统计信息
        self._print_conversation_stats(self.current_conversation)

        self.current_conversation = None

    def _print_conversation_stats(self, stats: ConversationStats):
        """
        输出对话统计信息

        Args:
            stats: 对话统计对象
        """
        duration = (stats.ended_at - stats.started_at).total_seconds()

        print("\n" + "=" * 60)
        print(f"📊 对话统计 [{stats.conversation_id}]")
        print("=" * 60)
        print(f"⏱️  耗时: {duration:.2f} 秒")
        print(f"📝 消息:")
        print(f"   - 开始时消息数: {stats.message_count_start}")
        print(f"   - 结束时消息数: {stats.message_count_end}")
        print(f"   - 本轮新增消息: {stats.message_count_added}")
        print(f"🔢 Token 消耗 (本轮):")
        print(f"   - 输入: {stats.token_usage.input_tokens:,}")
        print(f"   - 输出: {stats.token_usage.output_tokens:,}")
        print(f"   - 总计: {stats.token_usage.total_tokens:,}")
        print(f"💰 总计 Token 消耗 (所有对话):")
        print(f"   - 输入: {self.total_token_usage.input_tokens:,}")
        print(f"   - 输出: {self.total_token_usage.output_tokens:,}")
        print(f"   - 总计: {self.total_token_usage.total_tokens:,}")
        print("=" * 60)

    def get_summary(self) -> dict:
        """
        获取监控摘要

        Returns:
            dict: 监控摘要信息
        """
        return {
            'total_conversations': self.total_conversations,
            'total_tokens': {
                'input': self.total_token_usage.input_tokens,
                'output': self.total_token_usage.output_tokens,
                'total': self.total_token_usage.total_tokens
            },
            'conversation_history': [
                {
                    'conversation_id': conv.conversation_id,
                    'started_at': conv.started_at.isoformat(),
                    'ended_at': conv.ended_at.isoformat() if conv.ended_at else None,
                    'token_usage': {
                        'input': conv.token_usage.input_tokens,
                        'output': conv.token_usage.output_tokens,
                        'total': conv.token_usage.total_tokens
                    },
                    'message_count_start': conv.message_count_start,
                    'message_count_end': conv.message_count_end,
                    'message_count_added': conv.message_count_added
                }
                for conv in self.conversation_history
            ]
        }

    def reset(self):
        """重置监控者"""
        self.total_token_usage = TokenUsage()
        self.conversation_history = []
        self.current_conversation = None
        self.total_conversations = 0
