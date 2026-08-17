"""
AI Manager - The central orchestrator of the AI Work OS.

The Manager Agent receives user goals, creates plans,
and coordinates specialist agents to accomplish work.
"""

import json
import re
from typing import List, Optional
from enum import Enum

from .llm_client import LLMClient


class GoalStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Task:
    """A single unit of work assigned to an agent."""

    def __init__(
        self,
        task_id: str,
        description: str,
        agent_type: str,
        depends_on: Optional[List[str]] = None,
    ):
        self.task_id = task_id
        self.description = description
        self.agent_type = agent_type
        self.depends_on = depends_on or []
        self.status = GoalStatus.PENDING
        self.result = None

    def __repr__(self):
        return f"Task({self.task_id}, {self.agent_type}, {self.status.value})"


class Plan:
    """A plan consisting of multiple tasks to achieve a goal."""

    def __init__(self, goal: str, tasks: Optional[List[Task]] = None):
        self.goal = goal
        self.tasks = tasks or []
        self.status = GoalStatus.PENDING

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_next_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (dependencies met)."""
        ready = []
        for task in self.tasks:
            if task.status != GoalStatus.PENDING:
                continue
            deps_met = all(
                any(
                    t.task_id == dep and t.status == GoalStatus.COMPLETED
                    for t in self.tasks
                )
                for dep in task.depends_on
            )
            if deps_met:
                ready.append(task)
        return ready

    def is_complete(self) -> bool:
        return all(t.status == GoalStatus.COMPLETED for t in self.tasks)


class AIManager:
    """
    The AI Manager orchestrates specialist agents to accomplish user goals.

    Usage:
        manager = AIManager()
        plan = manager.create_plan("Write a business proposal for ABC Corp")
        manager.execute_plan(plan)
    """

    def __init__(self, llm: Optional[LLMClient] = None):
        self.active_goals: dict = {}
        self.agent_registry = {}
        # The AI "brain" — defaults to a real client (needs OPENROUTER_API_KEY).
        self.llm = llm or LLMClient()

    def register_agent(self, agent_type: str, agent_instance):
        """Register a specialist agent with the manager."""
        self.agent_registry[agent_type] = agent_instance

    def create_plan(self, goal: str) -> Plan:
        """
        Analyze a user goal and create an execution plan.

        Uses the AI to break the goal into tasks and pick which
        specialist agent should handle each one.
        """
        plan = Plan(goal=goal)
        plan.status = GoalStatus.PLANNING

        if not self.llm.is_configured():
            # No API key yet — return an empty plan and tell the user.
            # (Keep this message ASCII-only: Windows consoles can't always
            # print emoji under the default cp1252 encoding.)
            print("[WARN] No OPENROUTER_API_KEY found. Add it to .env to enable AI planning.")
            return plan

        tasks = self._plan_with_llm(goal)
        for task_data in tasks:
            plan.add_task(
                Task(
                    task_id=task_data.get("id", f"task-{len(plan.tasks) + 1}"),
                    description=task_data.get("description", goal),
                    agent_type=task_data.get("agent", "developer"),
                    depends_on=task_data.get("depends_on", []),
                )
            )
        return plan

    def _plan_with_llm(self, goal: str) -> List[dict]:
        """
        Ask the AI to decompose a goal into JSON tasks.

        The AI replies with something like:
          [{"id": "t1", "description": "...", "agent": "research",
            "depends_on": []}, ...]
        We parse it safely, falling back to an empty list on any failure.
        """
        system_prompt = (
            "You are the AI Manager of a work operating system. "
            "Break the user's goal into 2-5 small tasks. For each task choose "
            "the best specialist agent from: research, analyst, writer, "
            "developer, executive_assistant.\n\n"
            "Reply ONLY with a JSON array (no markdown), where each item is:\n"
            '{"id": "t1", "description": "short action", '
            '"agent": "one of the agents", "depends_on": ["t1"]}\n'
            "Use depends_on to list earlier task ids this task needs first."
        )
        raw = self.llm.chat(
            messages=[{"role": "user", "content": goal}],
            system_prompt=system_prompt,
        )
        return self._parse_tasks(raw)

    def _parse_tasks(self, raw: str) -> List[dict]:
        """Turn the AI's JSON reply into a list of task dicts (safe parser)."""
        try:
            # Strip markdown code fences if the AI wrapped the JSON in them.
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            data = json.loads(cleaned)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            print("⚠️  AI returned invalid JSON for the plan; starting with an empty plan.")
        return []

    def execute_plan(self, plan: Plan) -> dict:
        """
        Execute a plan by coordinating specialist agents.

        Routes tasks to appropriate agents, handles dependencies,
        and collects results.
        """
        plan.status = GoalStatus.IN_PROGRESS

        while not plan.is_complete():
            next_tasks = plan.get_next_tasks()
            if not next_tasks and not plan.is_complete():
                plan.status = GoalStatus.BLOCKED
                break

            for task in next_tasks:
                task.status = GoalStatus.IN_PROGRESS
                agent = self.agent_registry.get(task.agent_type)
                if agent:
                    task.result = agent.execute(task.description)
                else:
                    task.result = f"No agent available for: {task.agent_type}"
                task.status = GoalStatus.COMPLETED

        if plan.is_complete():
            plan.status = GoalStatus.VERIFYING
            plan.status = GoalStatus.COMPLETED

        return {"goal": plan.goal, "status": plan.status.value, "tasks": plan.tasks}

    def get_status(self, goal_id: str) -> Optional[GoalStatus]:
        """Check the status of an active goal."""
        return self.active_goals.get(goal_id)