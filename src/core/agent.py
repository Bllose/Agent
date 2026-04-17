import os
import json
import datetime
import platform
import uuid
import traceback
from anthropic import Anthropic

from src.tools import get_all_tools, execute_tool, load_tool
from src.tools.sub_agent import create_sub_agent, execute_sub_agent
from src.core.logger import get_logger
from src.core.monitor import AgentMonitor
from src.skills import SkillManager

DYNAMIC_BOUNDARY = "=== DYNAMIC_BOUNDARY ==="
SYSTEM_PROMPT_TEMPLATE = ""

class Agent:
    """Main Agent class for managing conversations and tool execution."""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        max_tokens: int = None
    ):
        """
        Initialize the Agent.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            base_url: Anthropic API base URL (defaults to ANTHROPIC_BASE_URL env var)
            model: Model to use for generation (defaults to MODEL env var)
            max_tokens: Maximum tokens for responses (defaults to MAX_TOKENS env var)
        """
        self.logger = get_logger('agent')

        # Get configuration from environment variables if not provided
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            self.logger.error("ANTHROPIC_API_KEY environment variable is not set")
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it in .env file or environment."
            )

        if base_url is None:
            base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

        if model is None:
            model = os.environ.get("MODEL", "claude-sonnet-4-6")

        if max_tokens is None:
            max_tokens_str = os.environ.get("MAX_TOKENS")
            max_tokens = int(max_tokens_str) if max_tokens_str else 4096

        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens

        # Load system prompt
        self.workplace = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.system_prompt = self._load_system_prompt()
        self.messages = []

        # Cache tool definitions
        self.tools = get_all_tools()

        # Initialize SKILL manager
        self.skill_manager = SkillManager(self.workplace)

        # Todo 任务管理
        self.todo_tasks = []
        self.current_todo_task = None

        # SubAgent 创建历史表（用于追踪子代理创建）
        # 格式: [{'subagent_id': str, 'message_index': int, 'task': str, 'created_at': str}]
        self.subagent_creation_history = []

        # 异常存储（用于状态保留）
        self.last_exception = None

        # 初始化监控者
        self.monitor = AgentMonitor()
        self.monitor.set_messages_reference(self.messages)

        self.logger.info(f"Agent initialized with model: {model}, max_tokens: {max_tokens}")

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

    def save_state(self):
        """
        保存 Agent 的状态到文件，包括：
        - Agent 消息历史
        - Todo 任务状态
        - 子代理创建历史（用于关联子代理状态文件）
        - 异常信息（如果存在）
        - 环境信息

        注意：SubAgent 的状态保存在独立的 sub_agent_{subagent_id}.json 文件中，
        通过 subagent_creation_history 中的记录进行逻辑关联。
        """
        # 构建完整状态
        state = {
            'timestamp': datetime.datetime.now().isoformat(),
            'agent_state': {
                'messages': self.serialize_messages(self.messages),
                'todo_tasks': self.todo_tasks,
                'current_todo_task': self.current_todo_task
            },
            'subagent_creation_history': self.subagent_creation_history,
            'exception': self.last_exception,
            'environment': {
                'model': self.model,
                'max_tokens': self.max_tokens,
                'workplace': self.workplace,
                'platform': platform.platform(),
                'system': platform.system(),
                'python_version': platform.python_version()
            }
        }

        # 保存到文件
        state_file = os.path.join(self.workplace, "agent_state.json")
        with open(state_file, "w", encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Agent state saved to {state_file}")

    def _build_system_prompt(self) -> str:
        global SYSTEM_PROMPT_TEMPLATE

        """Load the system prompt from templates."""
        template_path = os.path.join(
            self.workplace,
            "templates",
            "system.md"
        )

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                SYSTEM_PROMPT_TEMPLATE = f.read()
        except FileNotFoundError:
            return "You are an AI Agent designed to help users with software engineering tasks."
        
        if not SYSTEM_PROMPT_TEMPLATE:
             SYSTEM_PROMPT_TEMPLATE = "You are an AI Agent designed to help users with software engineering tasks."

        return SYSTEM_PROMPT_TEMPLATE

    def _build_system_prompt_with_todo(self) -> str:
        """
        构建包含 todo 任务状态和 SKILL 的 system prompt

        Returns:
            str: 完整的 system prompt
        """
        system_prompt_list = []

        if not SYSTEM_PROMPT_TEMPLATE:
            self._build_system_prompt()
        system_prompt_list.append(SYSTEM_PROMPT_TEMPLATE)

        # 添加 SKILL 摘要（如果有 SKILL）
        skills_summary = self.skill_manager.get_skills_summary()
        if skills_summary:
            system_prompt_list.append("\n")
            system_prompt_list.append(DYNAMIC_BOUNDARY)
            system_prompt_list.append("\n")
            system_prompt_list.append(skills_summary)

        # 添加 todo 任务状态（如果有任务）
        if self.todo_tasks:
            system_prompt_list.append("\n")
            system_prompt_list.append(DYNAMIC_BOUNDARY)
            system_prompt_list.append("\n")
            system_prompt_list.append(self.get_current_todo_status())

        # 添加动态上下文
        system_prompt_list.append("\n")
        system_prompt_list.append(DYNAMIC_BOUNDARY)
        system_prompt_list.append(self._build_dynamic_context())

        return "\n".join(system_prompt_list)

    def _load_system_prompt(self) -> str:
        """Load the system prompt from templates."""
        template_path = os.path.join(
            self.workplace,
            "templates",
            "system.md"
        )

        system_prompt_list = []

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                system_prompt_list.append(f.read())
        except FileNotFoundError:
            return "You are an AI Agent designed to help users with software engineering tasks."
        
        system_prompt_list.append(DYNAMIC_BOUNDARY)
        system_prompt_list.append(self._build_dynamic_context())

        return "\n".join(system_prompt_list)

    def _build_dynamic_context(self) -> str:
        lines = [
            f"Current date: {datetime.date.today().isoformat()}",
            f"Working directory: {self.workplace}",
            f"Platform: {platform.platform()}",
        ]
        return "# Dynamic context\n" + "\n".join(lines)

    def reset_conversation(self):
        """Reset the conversation history."""
        self.messages = []

    def clear_todo_tasks(self):
        """清除所有 todo 任务"""
        self.todo_tasks = []
        self.current_todo_task = None

    def get_current_todo_status(self) -> str:
        """
        获取当前 todo 任务状态

        Returns:
            str: todo 任务状态的格式化字符串
        """
        if not self.todo_tasks:
            return "当前没有活跃的任务计划"

        # 统计任务状态
        pending = sum(1 for t in self.todo_tasks if t.get('status') == 'pending')
        in_progress = sum(1 for t in self.todo_tasks if t.get('status') == 'in_progress')
        completed = sum(1 for t in self.todo_tasks if t.get('status') == 'completed')
        total = len(self.todo_tasks)

        status_lines = [
            f"## 当前进度",
            f"总计: {total} 个任务 | 完成: {completed} | 进行中: {in_progress} | 待处理: {pending}",
            ""
        ]

        # 显示下一个待处理的任务
        next_task = None
        for task in self.todo_tasks:
            if task.get('status') in ['pending', 'in_progress']:
                next_task = task
                break

        if next_task:
            status_lines.append(f"**当前应该完成的任务:**")
            status_lines.append(f"- 任务 ID {next_task['id']}: {next_task['content']}")
            status_lines.append(f"  状态: {next_task['status']}")
            status_lines.append("")

        # 显示任务列表
        status_lines.append("**任务列表:**")
        for task in self.todo_tasks:
            status_emoji = {
                'pending': '⬜',
                'in_progress': '🔄',
                'completed': '✅'
            }.get(task.get('status', 'pending'), '⬜')

            status_lines.append(f"{status_emoji} 任务 {task['id']}: {task['content']}")

        return "\n".join(status_lines)

    def get_next_todo_task(self) -> dict:
        """
        获取下一个待处理的 todo 任务

        Returns:
            dict: 下一个任务的信息，如果没有则返回 None
        """
        for task in self.todo_tasks:
            if task.get('status') in ['pending', 'in_progress']:
                return task
        return None

    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return the Agent's response.

        Args:
            user_message: The user's input message

        Returns:
            The Agent's response text
        """
        # 生成对话 ID
        conversation_id = str(uuid.uuid4())
        self.monitor.start_conversation(conversation_id)

        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Run the agent loop until no more tool use
            result = self._run_agent_loop()
            return result
        finally:
            self.monitor.end_conversation()

    def _handle_sub_agent_call(self, tool_input: dict, block_id: str) -> dict:
        """
        处理 SubAgent 工具调用

        Args:
            tool_input: sub_agent 工具的输入参数
            block_id: 工具调用的 block ID

        Returns:
            dict: SubAgent 执行结果
        """
        try:
            task = tool_input.get('task')
            context = tool_input.get('context')

            if not task:
                self.logger.error("sub_agent task parameter is required")
                return {
                    "success": False,
                    "error": "task parameter is required for sub_agent"
                }

            self.logger.info(f"Starting sub-agent task: {task[:50]}...")

            # 生成唯一的 SubAgent ID
            subagent_id = str(uuid.uuid4())

            # 记录 SubAgent 创建历史（在记录前就记录，确保即使创建失败也能追踪）
            self.subagent_creation_history.append({
                'subagent_id': subagent_id,
                'message_index': len(self.messages),  # 当前消息的索引
                'task': task,
                'created_at': datetime.datetime.now().isoformat()
            })

            # 创建 SubAgent
            subagent = create_sub_agent(
                task=task,
                context=context,
                parent_agent=self,
                subagent_id=subagent_id
            )

            # 执行 SubAgent
            result = execute_sub_agent(subagent)

            # 将 subagent_id 附加到结果中，供主 Agent 记录
            result['subagent_id'] = subagent_id

            if result.get('success'):
                self.logger.info("Sub-agent task completed successfully")
            else:
                self.logger.error(f"Sub-agent task failed: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"Sub-agent execution exception: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"SubAgent execution failed: {str(e)}"
            }

    def _run_agent_loop(self) -> str:
        """
        Run the agent loop: request model, handle tools, repeat until done.
        Returns:
            The final text response from the model
        """
        while True:
            # 构建包含 todo 任务的 system prompt
            system_prompt = self._build_system_prompt_with_todo()

            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=self.messages,
                tools=self.tools,
                max_tokens=self.max_tokens
            )

            # 记录 token 使用情况
            if hasattr(response, 'usage'):
                self.monitor.record_token_usage({
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                })

            # Check if response contains tool_use
            has_tool_use = False
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    has_tool_use = True

                    # 动态加载工具（如果还未加载）
                    load_tool(block.name)

                    # 特殊处理 SubAgent 调用
                    if block.name == "sub_agent":
                        tool_result = self._handle_sub_agent_call(block.input, block.id)
                        subagent_id = tool_result.get('subagent_id')
                    else:
                        # Execute tool
                        tool_result = execute_tool(block.name, block.input)
                        subagent_id = None

                    # 处理 todo 工具的结果，同步到 Agent 的 todo_tasks 中
                    if block.name == "todo" and tool_result.get('success'):
                        action = block.input.get('action')
                        if action == "create":
                            tasks = tool_result.get('tasks', [])
                            self.todo_tasks.extend(tasks)
                            self.logger.info(f"Added {len(tasks)} tasks to todo plan")
                        elif action == "update":
                            task_id = block.input.get('task_id')
                            if 'status' in block.input:
                                new_status = block.input['status']
                                # 更新内存中的任务状态
                                for task in self.todo_tasks:
                                    if task.get('id') == task_id:
                                        old_status = task.get('status')
                                        task['status'] = new_status
                                        self.logger.info(f"Task {task_id} status updated from {old_status} to {new_status}")
                                        break

                    # Convert result dict to JSON string for the API
                    result_content = tool_result.copy()
                    # 如果有 subagent_id，附加到结果中以便后续引用
                    if subagent_id:
                        result_content['_subagent_id'] = subagent_id

                    tool_results.append({
                        "tool_use_id": block.id,
                        "content": json.dumps(result_content, ensure_ascii=False)
                    })
                elif block.type == "text":
                    # 处理文本块，继续循环直到没有工具调用
                    text_first_line = block.text.strip().splitlines()[0] if block.text.strip() else ""
                    self.logger.info(f"Received text block: {text_first_line} ...")

            # Add assistant response to history
            self.messages.append({
                "role": "assistant",
                "content": response.content
            })
        
            # If there were tool calls, add results to history and continue loop
            if has_tool_use:
                for result in tool_results:
                    self.messages.append({
                        "role": "user",
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                # Continue to next iteration to get model's follow-up
                continue

            # No tool use, model is done - extract and return text
            text_output = ""
            for block in response.content:
                if block.type == "text":
                    text_output += block.text

            return text_output