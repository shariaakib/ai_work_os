#!/usr/bin/env python3
"""
AI Work OS - Main Entry Point

An AI-native operating system for professional work.
"""

import sys
from pathlib import Path

# Fix emoji/unicode on Windows: force UTF-8 output even when stdout is a
# pipe (default cp1252 can't encode emoji like 🚀 and crashes).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.ai_manager import AIManager, Plan
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
from src.permissions.permission_manager import PermissionManager
from src.verification.verifier import Verifier


class AIWorkOS:
    """
    The main AI Work OS class that ties everything together.

    Usage:
        os = AIWorkOS()
        os.manager.create_plan("Prepare meeting briefing")
        os.run()
    """

    def __init__(self):
        print("🚀 Initializing AI Work OS...")

        # Core systems
        self.memory = WorkMemory()
        self.work_graph = WorkGraph()
        self.permissions = PermissionManager()
        self.verifier = Verifier()

        # AI Manager
        self.llm = LLMClient()
        self.manager = AIManager(llm=self.llm)

        # Register specialist agents
        self._register_agents()

        print("✅ AI Work OS ready!")

    def _register_agents(self):
        """Register all specialist agents with the manager."""
        self.manager.register_agent("research", ResearchAgent())
        self.manager.register_agent("analyst", AnalystAgent())
        self.manager.register_agent("writer", WriterAgent())
        self.manager.register_agent("developer", DeveloperAgent())
        self.manager.register_agent("executive_assistant", ExecutiveAssistantAgent())

    def process_goal(self, goal: str) -> dict:
        """
        Process a user goal end-to-end.

        1. Check memory for context
        2. Create a plan
        3. Execute through agents
        4. Verify results
        5. Return result
        """
        print(f"\n🎯 Processing goal: {goal}")
        print("📋 Creating plan...")

        plan = self.manager.create_plan(goal)
        print("🚀 Executing plan...")

        result = self.manager.execute_plan(plan)
        print(f"✅ Goal completed: {result['status']}")

        return result

    def run(self):
        """Start the interactive AI Work OS session."""
        print("\n" + "=" * 50)
        print("🤖 AI Work OS — Ready")
        print('Type "exit" to quit')
        print("=" * 50)

        while True:
            try:
                goal = input("\n🎯 What would you like to do? > ").strip()
                if goal.lower() in ("exit", "quit", "q"):
                    print("👋 Shutting down AI Work OS...")
                    break
                if goal:
                    self.process_goal(goal)
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    os = AIWorkOS()

    if "--chat" in sys.argv:
        # Phase 2 quick test: type a message, AI answers.
        # Usage: python main.py --chat
        print("\n🤖 AI chat started. Type 'exit' to quit.")
        while True:
            # Support piped input (e.g. `echo "hi" | python main.py --chat`)
            # so the AI can be tested non-interactively.
            user_input = input("You: ").strip()
            if user_input.lower() in ("exit", "quit", "q"):
                break
            if user_input:
                reply = os.llm.chat(messages=[{"role": "user", "content": user_input}])
                print(f"AI: {reply}")
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