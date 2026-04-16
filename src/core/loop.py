import datetime
import traceback
from .agent import Agent
from .logger import get_logger

MAX_RETRY = 1

class AgentLoop:
    """Main Agent Loop for REPL interaction."""

    def __init__(self, agent: Agent):
        """
        Initialize the Agent Loop.
        Args:
            agent: The Agent instance to use
        """
        self.agent = agent
        self.retry_count = 0
        self.is_retrying = False
        self.logger = get_logger('agent.loop')

    def start(self):
        """Start the interactive loop."""
        self.logger.info("Agent Loop started. Type 'exit' or 'quit' to leave.")
        print("Agent Loop started. Type 'exit' or 'quit' to leave.")
        print("-" * 50)

        while True:
            try:
                if self.retry_count >= MAX_RETRY:
                    self.logger.error("Maximum retry limit reached. Saving state and exiting.")
                    print("Maximum retry limit reached. Saving state and exiting.")
                    self.agent.save_state()
                    print("State saved. Exiting.")
                    break

                # Get user input
                if not self.is_retrying:
                    user_input = input(">>> ").strip()
                else:
                    self.is_retrying = False

                if not user_input:
                    continue

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit']:
                    self.logger.info("User requested exit")
                    print("Goodbye!")
                    break

                # Check for special commands
                if user_input.lower() == 'status':
                    self._show_status()
                    continue

                if user_input.lower() == 'clear':
                    self.agent.reset_conversation()
                    self.logger.info("Conversation history cleared")
                    print("Conversation history cleared.")
                    continue

                if user_input.lower() == 'todos':
                    todos = self.agent.get_current_todo_status()
                    print(todos)
                    continue

                # Process the message
                self.logger.info(f"Processing user message: {user_input[:50]}...")
                print("\nProcessing...")
                response = self.agent.process_message(user_input)

                # Display response
                print("\n" + response)
                print("-" * 50)

            except KeyboardInterrupt:
                self.logger.info("KeyboardInterrupt received")
                print("\nUse 'exit' or 'quit' to leave.")
            except Exception as e:
                # 存储异常信息到 agent
                self.agent.last_exception = {
                    'type': type(e).__name__,
                    'message': str(e),
                    'traceback': traceback.format_exc(),
                    'timestamp': datetime.datetime.now().isoformat()
                }

                self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
                self.retry_count += 1
                self.is_retrying = True
                user_input = "上个步骤执行异常，异常信息: " + str(e) + "，请重新执行上个步骤，注意修正错误。"

    def _show_status(self):
        """显示当前 Agent 状态"""
        self.logger.info(f"Agent Status: Messages={len(self.agent.messages)}, Todos={len(self.agent.todo_tasks)}")
        print("\n=== Agent Status ===")
        print(f"Message count: {len(self.agent.messages)}")
        print(f"Todo tasks: {len(self.agent.todo_tasks)}")

        if self.agent.todo_tasks:
            print("\nTodo Tasks:")
            for task in self.agent.todo_tasks:
                status_emoji = {
                    'pending': '⬜',
                    'in_progress': '🔄',
                    'completed': '✅'
                }.get(task.get('status', 'pending'), '⬜')
                print(f"  {status_emoji} [{task['id']}] {task['content']}")

        print("=" * 30)
