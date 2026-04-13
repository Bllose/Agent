import os
import json
from anthropic import Anthropic

from src.tools import get_all_tools, execute_tool


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
        self.system_prompt = self._load_system_prompt()
        self.messages = []

        # Cache tool definitions
        self.tools = get_all_tools()

    def _load_system_prompt(self) -> str:
        """Load the system prompt from templates."""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "templates",
            "system.md"
        )
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "You are an AI Agent designed to help users with software engineering tasks."

    def reset_conversation(self):
        """Reset the conversation history."""
        self.messages = []

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
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                system=self.system_prompt,
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
