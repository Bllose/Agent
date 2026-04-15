import os
import json
import datetime
import platform
from anthropic import Anthropic

from src.tools import get_all_tools, execute_tool

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
        # Get configuration from environment variables if not provided
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
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

        # Todo 任务管理
        self.todo_tasks = []
        self.current_todo_task = None

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
        构建包含 todo 任务状态的 system prompt

        Returns:
            str: 完整的 system prompt
        """
        system_prompt_list = []

        if not SYSTEM_PROMPT_TEMPLATE:
            self._build_system_prompt()
        system_prompt_list.append(SYSTEM_PROMPT_TEMPLATE)

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
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        # Run the agent loop until no more tool use
        return self._run_agent_loop()

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

            # Check if response contains tool_use
            has_tool_use = False
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    has_tool_use = True
                    # Execute tool
                    tool_result = execute_tool(block.name, block.input)

                    # 如果是 todo_create，将任务保存到 Agent 的 todo_tasks 中
                    if block.name == "todo_create" and tool_result.get('success'):
                        tasks = tool_result.get('tasks', [])
                        self.todo_tasks.extend(tasks)
                        print(f"[TODO] 已将 {len(tasks)} 个任务添加到计划中")

                    # 如果是 todo_update，更新 Agent 内存中的任务状态
                    if block.name == "todo_update" and tool_result.get('success'):
                        task_id = block.input.get('task_id')
                        if 'status' in block.input:
                            new_status = block.input['status']
                            # 更新内存中的任务状态
                            for task in self.todo_tasks:
                                if task.get('id') == task_id:
                                    old_status = task.get('status')
                                    task['status'] = new_status
                                    print(f"[TODO] 任务 {task_id} 状态从 {old_status} 更新为 {new_status}")
                                    break

                    # Convert result dict to JSON string for the API
                    tool_results.append({
                        "tool_use_id": block.id,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })

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
