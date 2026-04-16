"""
SubAgent 工具模块

提供 SubAgent 类和 sub_agent 工具函数，用于将子任务委托给独立的 Agent 实例执行。
"""
import json
import os
import datetime
import traceback
from anthropic import Anthropic
from src.core.logger import get_logger

logger = get_logger('agent.tools.sub_agent')

# SubAgent 重试次数上限
SUBAGENT_MAX_RETRY = 1


class SubAgent:
    """
    SubAgent 类，用于执行独立的子任务。

    SubAgent 是一个轻量级的 Agent 实例，专门用于处理特定的子任务。
    它拥有独立的上下文和消息历史，执行完毕后将结果返回给主 Agent。
    """
    
    def __init__(
        self,
        task: str,
        parent_agent_config: dict,
        parent_agent=None,
        subagent_id: str = None,
        context: str = None,
        tools: list = None
    ):
        """
        初始化 SubAgent

        Args:
            task: 要执行的子任务描述
            parent_agent_config: 主 Agent 的配置（api_key, base_url, model, max_tokens）
            parent_agent: 主 Agent 实例（用于状态同步）
            subagent_id: SubAgent 的唯一标识
            context: 额外的上下文信息
            tools: 可用的工具列表，如果为 None 则使用主 Agent 的工具
        """
        self.task = task
        self.context = context or ""
        self.parent_agent = parent_agent
        self.subagent_id = subagent_id

        # 使用主 Agent 的配置
        self.client = Anthropic(
            api_key=parent_agent_config.get('api_key'),
            base_url=parent_agent_config.get('base_url')
        )
        self.model = parent_agent_config.get('model')
        self.max_tokens = parent_agent_config.get('max_tokens')
        self.workplace = parent_agent_config.get('workplace')

        # 独立的消息历史
        self.messages = []

        # 构建系统提示
        self.system_prompt = self._build_system_prompt()

        # 可用工具
        self.tools = tools or []

        # 执行结果
        self.result = None

        # 重试计数器
        self.retry_count = 0

        logger.info(f"SubAgent {subagent_id} initialized for task: {task[:50]}...")
        
    def _build_system_prompt(self) -> str:
        """
        构建 SubAgent 的系统提示
        
        Returns:
            str: 系统提示字符串
        """
        base_prompt = """你是一个专门处理特定子任务的 AI Agent。

你的任务是专注地完成分配给你的子任务，然后将结果返回给主 Agent。

## 指导原则
1. 专注子任务：只专注于完成你被分配的任务，不要超出范围
2. 简洁高效：尽量用最少的步骤完成任务
3. 清晰反馈：完成后提供清晰的总结和结果
4. 自主执行：根据需要使用可用工具完成任务

## 返回格式
完成任务后，提供以下格式的总结：
- 任务描述
[你执行的任务描述]

- 执行步骤
[你采取的主要步骤]

- 结果
[任务的最终结果]

- 相关文件/输出
[如果适用，列出修改的文件或生成的输出]
"""
        
        if self.context:
            base_prompt += f"\n\n## 任务上下文\n{self.context}"
        
        return base_prompt

    def serialize_messages(self, messages) -> list:
        """
        序列化消息对象（处理不能直接序列化的对象）

        Args:
            messages: 消息列表

        Returns:
            list: 可序列化的消息列表
        """
        serialized = []
        for msg in messages:
            if isinstance(msg, dict):
                serialized_msg = {}
                for key, value in msg.items():
                    if key == 'content':
                        # 处理 content 可能是 TextBlock 或 ToolUseBlock 对象
                        if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                            # 这是一个 block 对象列表
                            content_list = []
                            for block in value:
                                if hasattr(block, '__dict__'):
                                    content_list.append({
                                        'type': getattr(block, 'type', 'unknown'),
                                        'text': getattr(block, 'text', ''),
                                        'input': getattr(block, 'input', {}),
                                        'id': getattr(block, 'id', ''),
                                        'name': getattr(block, 'name', '')
                                    })
                                else:
                                    content_list.append(str(block))
                            serialized_msg[key] = content_list
                        else:
                            serialized_msg[key] = value
                    else:
                        serialized_msg[key] = value
                serialized.append(serialized_msg)
            else:
                serialized.append(str(msg))
        return serialized

    def save_state(self, exception: Exception):
        """
        保存 SubAgent 状态到独立文件

        Args:
            exception: 捕获的异常对象
        """
        if not self.workplace or not self.subagent_id:
            logger.warning("Cannot save SubAgent state: workplace or subagent_id is missing")
            return

        state = {
            'subagent_id': self.subagent_id,
            'task': self.task,
            'context': self.context,
            'messages': self.serialize_messages(self.messages),
            'retry_count': self.retry_count,
            'exception': {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            },
            'model': self.model,
            'max_tokens': self.max_tokens,
            'timestamp': datetime.datetime.now().isoformat()
        }

        # 保存到独立文件
        state_file = os.path.join(self.workplace, f"sub_agent_{self.subagent_id}.json")
        with open(state_file, "w", encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        logger.info(f"SubAgent state saved to {state_file}")

    def execute(self) -> dict:
        """
        执行子任务

        Returns:
            dict: 包含执行结果的字典
                - success: bool 是否成功
                - task: str 任务描述描述
                - steps: list 执行步骤
                - result: str 最终结果
                - messages: str 完整的消息历史
                - error: str 错误信息（如果失败）
        """
        logger.info(f"Executing subtask: {self.task[:50]}...")

        while self.retry_count <= SUBAGENT_MAX_RETRY:
            try:
                # 如果不是第一次执行（重试中），修改任务描述
                if self.retry_count > 0:
                    retry_message = f"\n\n【重试 #{self.retry_count}】上一次执行失败，请重新执行任务并修正错误。"
                else:
                    retry_message = ""

                # 添加任务到消息历史（仅第一次）
                if self.retry_count == 0:
                    self.messages.append({
                        "role": "user",
                        "content": f"请完成以下任务：\n\n{self.task}{retry_message}"
                    })
                else:
                    # 重试时，添加重试消息
                    self.messages.append({
                        "role": "user",
                        "content": retry_message
                    })

                # 调用模型
                response = self.client.messages.create(
                    model=self.model,
                    system=self.system_prompt,
                    messages=self.messages,
                    tools=self.tools,
                    max_tokens=self.max_tokens
                )

                # 处理工具调用
                while True:
                    # 检查是否有工具调用
                    has_tool_use = False
                    tool_results = []

                    for block in response.content:
                        if block.type == "tool_use":
                            has_tool_use = True
                            logger.debug(f"SubAgent tool call: {block.name}")
                            # 这里需要导入 execute_tool 函数
                            from src.tools import execute_tool
                            tool_result = execute_tool(block.name, block.input)
                            tool_results.append({
                                "tool_use_id": block.id,
                                "content": str(tool_result)
                            })

                    # 添加助手响应到历史
                    self.messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    # 如果有工具调用，添加结果并继续
                    if has_tool_use:
                        for result in tool_results:
                            self.messages.append({
                                "role": "user",
                                "content": json.dumps(result, ensure_ascii=False)
                            })

                        # 继续对话
                        response = self.client.messages.create(
                            model=self.model,
                            system=self.system_prompt,
                            messages=self.messages,
                            tools=self.tools,
                            max_tokens=self.max_tokens
                        )
                        continue

                    # 没有工具调用，提取最终响应
                    break

                # 提取文本输出
                text_output = ""
                for block in response.content:
                    if block.type == "text":
                        text_output += block.text

                self.result = {
                    "success": True,
                    "task": self.task,
                    "result": text_output,
                    "message_count": len(self.messages),
                    "retry_count": self.retry_count
                }

                logger.info(f"Subtask completed successfully. {len(self.messages)} messages processed")
                return self.result

            except Exception as e:
                logger.error(f"Subtask execution failed (retry {self.retry_count}/{SUBAGENT_MAX_RETRY}): {str(e)}", exc_info=True)
                self.retry_count += 1

                # 如果达到重试上限，保存状态并返回
                if self.retry_count > SUBAGENT_MAX_RETRY:
                    # 保存状态到独立文件
                    self.save_state(e)

                    self.result = {
                        "success": False,
                        "task": self.task,
                        "error": str(e),
                        "retry_count": self.retry_count,
                        "state_saved": True,
                        "state_file": f"sub_agent_{self.subagent_id}.json"
                    }
                    return self.result

                # 继续重试
                logger.info(f"Retrying subtask... ({self.retry_count}/{SUBAGENT_MAX_RETRY})")
                continue


def create_sub_agent(task: str, context: str = None, parent_agent=None, subagent_id: str = None) -> SubAgent:
    """
    创建 SubAgent 实例（不执行）

    Args:
        task: 要执行的子任务描述
        context: 额外的上下文信息
        parent_agent: 主 Agent 实例（用于获取配置和工具）
        subagent_id: SubAgent 的唯一标识

    Returns:
        SubAgent: 创建的 SubAgent 实例

    Raises:
        ValueError: 如果 parent_agent 为 None
    """
    if parent_agent is None:
        raise ValueError("parent_agent is required")

    # 获取主 Agent 的配置
    parent_config = {
        'api_key': parent_agent.client.api_key,
        'base_url': parent_agent.client.base_url,
        'model': parent_agent.model,
        'max_tokens': parent_agent.max_tokens,
        'workplace': parent_agent.workplace
    }

    # 创建 SubAgent 实例
    subagent = SubAgent(
        task=task,
        parent_agent_config=parent_config,
        parent_agent=parent_agent,
        subagent_id=subagent_id,
        context=context,
        tools=parent_agent.tools
    )

    return subagent


def execute_sub_agent(subagent: SubAgent) -> dict:
    """
    执行 SubAgent

    Args:
        subagent: SubAgent 实例

    Returns:
        dict: SubAgent 的执行结果
    """
    try:
        result = subagent.execute()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute SubAgent: {str(e)}"
        }


def sub_agent(task: str, context: str = None, parent_agent=None, subagent_id: str = None) -> dict:
    """
    创建并执行 SubAgent 的工具函数（向后兼容）

    Args:
        task: 要执行的子任务描述
        context: 额外的上下文信息
        parent_agent: 主 Agent 实例（用于获取配置和工具）
        subagent_id: SubAgent 的唯一标识

    Returns:
        dict: SubAgent 的执行结果
    """
    try:
        # 创建 SubAgent
        subagent = create_sub_agent(
            task=task,
            context=context,
            parent_agent=parent_agent,
            subagent_id=subagent_id
        )

        # 执行 SubAgent
        result = execute_sub_agent(subagent)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create and execute SubAgent: {str(e)}"
        }
