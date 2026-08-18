#!/usr/bin/env python3
"""
AI Work OS - Main Entry Point

An AI-native operating system for professional work.
"""

import logging
import sys
from pathlib import Path

# Fix emoji/unicode on Windows: force UTF-8 output even when stdout is a pipe
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is importable
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.core.ai_manager import AIManager
from src.core.llm_client import LLMClient
from src.core.work_graph import WorkGraph, WorkNode
from src.core.memory import WorkMemory
from src.agents.specialist_agents import (
    ResearchAgent,
    AnalystAgent,
    WriterAgent,
    DeveloperAgent,
    ExecutiveAssistantAgent,
)
from src.agents.custom_agent import CustomAgent
from src.permissions.permission_manager import PermissionManager
from src.verification.verifier import Verifier

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are AI Work OS, an AI-native operating system for professional work. "
    "You help users accomplish goals through planning, specialist agents, "
    "and task automation. Be direct and helpful."
)


class AIWorkOS:
    """The main AI Work OS class that ties everything together.

    Usage:
        os = AIWorkOS()
        os.manager.create_plan("Prepare meeting briefing")
        os.run()
    """

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        )
        logger.info("AI Work OS starting")
        print("[AI Work OS] Initializing...")

        # Core systems
        self.memory = WorkMemory()
        self.work_graph = WorkGraph()
        self.permissions = PermissionManager()
        self.verifier = Verifier()

        # AI Manager - wires all subsystems together
        self.llm = LLMClient()
        self.manager = AIManager(
            llm=self.llm,
            memory=self.memory,
            work_graph=self.work_graph,
            verifier=self.verifier,
            permissions=self.permissions,
        )

        # Register specialist agents
        self._register_agents()

        print("[AI Work OS] Ready!")

    def _register_agents(self):
        """Register all specialist agents with the manager."""
        llm = self.llm
        self.manager.register_agent("research", ResearchAgent(llm=llm))
        self.manager.register_agent("analyst", AnalystAgent(llm=llm))
        self.manager.register_agent("writer", WriterAgent(llm=llm))
        self.manager.register_agent("developer", DeveloperAgent(llm=llm))
        self.manager.register_agent("executive_assistant", ExecutiveAssistantAgent(llm=llm))
        self.manager.register_agent("custom", CustomAgent(llm=llm))
        logger.info("All agents registered")

    def process_goal(self, goal: str) -> dict:
        """Process a user goal end-to-end.

        1. Check memory for context
        2. Create a plan
        3. Execute through agents
        4. Verify results
        5. Return result
        """
        print(f"\n[AI Work OS] Processing goal: {goal}")
        print("[AI Work OS] Creating plan...")

        plan = self.manager.create_plan(goal)
        print(f"[AI Work OS] Plan created with {len(plan.tasks)} tasks")

        print("[AI Work OS] Executing plan...")
        result = self.manager.execute_plan(plan)
        print(f"[AI Work OS] Goal completed: {result['status']}")

        return result

    def run(self):
        """Start the interactive AI Work OS session."""
        print("\n" + "=" * 50)
        print("[AI Work OS] Ready (interactive mode)")
        print('Type "exit" to quit')
        print("=" * 50)

        while True:
            try:
                goal = input("\n> What would you like to do? ").strip()
                if goal.lower() in ("exit", "quit", "q"):
                    print("[AI Work OS] Shutting down...")
                    break
                if goal:
                    self.process_goal(goal)
            except KeyboardInterrupt:
                print("\n[AI Work OS] Goodbye!")
                break
            except Exception as e:
                logger.error("Error during goal processing: %s", str(e))
                print(f"[ERROR] {e}")


def chat_mode(os: AIWorkOS):
    """Run the chat interface for direct Q&A mode."""
    print("\n[AI Work OS] AI chat started. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        if user_input.lower() in ("exit", "quit", "q"):
            break
        if not user_input:
            continue

        # Dedicated to Munira
        lowered = user_input.lower()
        if any(kw in lowered for kw in [
            "who is the one akib love", "akib love most", "akib's love",
            "who akib love", "munira"
        ]):
            print("AI: Munira - the one Akib loves most, dedicated to his girlfriend.")
            continue

        try:
            reply = os.llm.chat(messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ])
            print(f"AI: {reply}")
        except Exception as e:
            logger.error("Chat error: %s", str(e))
            print(f"[ERROR] {e}")


def main():
    """Main entry point.

    Usage:
        python main.py                  # Interactive work mode
        python main.py --chat           # Chat mode (Q&A)
        python main.py "do a thing"     # Process a single goal
    """
    os = AIWorkOS()

    if "--chat" in sys.argv:
        chat_mode(os)
        return

    if len(sys.argv) > 1:
        # Process a single goal from command line
        goal = " ".join(sys.argv[1:])
        result = os.process_goal(goal)
        print(f"\nResult: {result}")
    else:
        # Interactive mode
        os.run()


if __name__ == "__main__":
    main()
