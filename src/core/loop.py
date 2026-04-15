from .agent import Agent

MAX_RETRY = 3

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

    def start(self):
        """Start the interactive loop."""
        print("Agent Loop started. Type 'exit' or 'quit' to leave.")
        print("-" * 50)

        while True:
            try:
                if self.retry_count >= MAX_RETRY:
                    self.agent.save_state()
                    print("Maximum retry limit reached. State saved. Exiting.")
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
                    print("Goodbye!")
                    break

                # Process the message
                response = self.agent.process_message(user_input)

                # Display response
                print("\n" + response)
                print("-" * 50)

            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to leave.")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                self.retry_count += 1
                self.is_retrying = True
                user_input = "上个步骤执行异常，异常信息: " + str(e) + "，请重新执行上个步骤，注意修正错误。"
