from .agent import Agent


class AgentLoop:
    """Main Agent Loop for REPL interaction."""

    def __init__(self, agent: Agent):
        """
        Initialize the Agent Loop.

        Args:
            agent: The Agent instance to use
        """
        self.agent = agent

    def start(self):
        """Start the interactive loop."""
        print("Agent Loop started. Type 'exit' or 'quit' to leave.")
        print("-" * 50)

        while True:
            try:
                # Get user input
                user_input = input(">>> ").strip()

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
                print(f"\nError: {str(e)}")
                print("-" * 50)
