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
from src.core.logger import initialize_logging, get_logger

# 初始化日志系统
logger = initialize_logging(
    name='agent',
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    log_dir=os.path.join(project_root, 'logs'),
    enable_console=True,
    enable_file=True
)


def main():
    """Main entry point for the Agent CLI."""
    try:
        # Initialize agent (configuration loaded from .env)
        logger.info("Initializing Agent...")
        agent = Agent()
        logger.info("Agent initialized successfully")

        # Start loop
        loop = AgentLoop(agent)
        loop.start()

        return 0

    except ValueError as e:
        logger.error(f"Configuration Error: {str(e)}")
        print("\nPlease create a .env.env file with your configuration:")
        print("  cp .env.example .env")
        print("  Then edit .env with your API key and settings.")
        return 1
    except KeyboardInterrupt:
        logger.info("Interrupted. Goodbye!")
        print("\nInterrupted. Goodbye!")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
