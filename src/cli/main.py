import sys
import os
from dotenv import load_dotenv

# Load .env file from project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

# Add parent directory to path to allow imports
sys.path.insert(0, project_root)

from src.core.agent import Agent
from src.core.loop import AgentLoop


def main():
    """Main entry point for the Agent CLI."""
    try:
        # Initialize agent (configuration loaded from .env)
        agent = Agent()

        # Start loop
        loop = AgentLoop(agent)
        loop.start()

        return 0

    except ValueError as e:
        print(f"Configuration Error: {str(e)}")
        print("\nPlease create a .env.env file with your configuration:")
        print("  cp .env.example .env")
        print("  Then edit .env with your API key and settings.")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
