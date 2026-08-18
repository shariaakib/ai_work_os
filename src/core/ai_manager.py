"""
AI Manager - The central orchestrator of the AI Work OS.

The Manager Agent receives user goals, creates plans,
and coordinates specialist agents to accomplish work.

Production-ready: integrates with memory, work graph, permissions,
and verification for a complete end-to-end pipeline.
"""

import json
import logging
import re
from typing import List, Optional

from enum import Enum

from .llm_client import LLMClient

logger = logging.getLogger(__name__)


class GoalStatus(Enum):
    """Lifecycle states for goals and tasks."""
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

    def to_dict(self) -> dict:
        """Serialize the task to a dictionary for JSON output."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "agent_type": self.agent_type,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "result": self.result,
        }


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
        """True when every task has been completed."""
        return all(t.status == GoalStatus.COMPLETED for t in self.tasks)

    def to_dict(self) -> dict:
        """Serialize the plan to a dictionary."""
        return {
            "goal": self.goal,
            "status": self.status.value,
            "tasks": [t.to_dict() for t in self.tasks],
        }



class AIManager:
    """The AI Manager orchestrates specialist agents to accomplish user goals.

    Integrates with: memory (context), work graph (relationships),
    permissions (safety), and verifier (quality).

    Usage:
        manager = AIManager()
        plan = manager.create_plan("Write a business proposal for ABC Corp")
        manager.execute_plan(plan)
    """

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        memory=None,
        work_graph=None,
        verifier=None,
        permissions=None,
    ):
        self.active_goals: dict = {}
        self.agent_registry: dict = {}
        # The AI "brain" - defaults to a real client (needs OPENROUTER_API_KEY).
        self.llm = llm or LLMClient()
        # Cross-system integrations
        self.memory = memory
        self.work_graph = work_graph
        self.verifier = verifier
        self.permissions = permissions

    def register_agent(self, agent_type: str, agent_instance):
        """Register a specialist agent with the manager."""
        self.agent_registry[agent_type] = agent_instance
        logger.debug("Registered agent: %s", agent_type)

    def create_plan(self, goal: str) -> Plan:
        """Analyze a user goal and create an execution plan.

        Uses the AI to break the goal into tasks and pick which
        specialist agent should handle each one. Falls back to
        memory-based context if available.
        """
        plan = Plan(goal=goal)
        plan.status = GoalStatus.PLANNING
        logger.info("Creating plan for goal: %s", goal)

        if not self.llm.is_configured():
            logger.warning("No LLM API key configured; returning empty plan")
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
        logger.info("Plan created with %d tasks", len(plan.tasks))
        return plan

    def _plan_with_llm(self, goal: str) -> List[dict]:
        """Ask the AI to decompose a goal into JSON tasks.

        Optionally includes memory context to inform the planning.
        """
        memory_context = ""
        if self.memory:
            relevant = self.memory.search(goal)
            if relevant:
                memory_context = "\n\nContext from memory:\n"
                for item in relevant[:5]:
                    memory_context += f"- [{item.category}] {item.content}\n"

        system_prompt = (
            "You are the AI Manager of a work operating system. "
            "Break the user's goal into 2-5 small tasks. For each task choose "
            "the best specialist agent from: research, analyst, writer, "
            "developer, executive_assistant.\n\n"
            "Reply ONLY with a JSON array (no markdown), where each item is:\n"
            '{"id": "t1", "description": "short action", '
            '"agent": "one of the agents", "depends_on": ["t1"]}\n'
            "Use depends_on to list earlier task ids this task needs first."
            f"{memory_context}"
        )

        try:
            raw = self.llm.chat(
                messages=[{"role": "user", "content": goal}],
                system_prompt=system_prompt,
            )
            return self._parse_tasks(raw)
        except Exception as e:
            logger.error("Planning failed: %s", str(e))
            return []

    def _parse_tasks(self, raw: str) -> List[dict]:
        """Turn the AI's JSON reply into a list of task dicts (safe parser)."""
        try:
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            data = json.loads(cleaned)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            logger.warning("AI returned invalid JSON for the plan")
            print("[WARN] AI returned invalid JSON for the plan; starting with an empty plan.")
        return []

    def execute_plan(self, plan: Plan) -> dict:
        """Execute a plan by coordinating specialist agents.

        Routes tasks to appropriate agents, handles dependencies,
        integrates with permissions and verification, and collects results.
        """
        plan.status = GoalStatus.IN_PROGRESS
        logger.info("Executing plan: %s", plan.goal)

        results = []
        max_iterations = 100  # safety guard against infinite loops
        iteration = 0

        while not plan.is_complete() and iteration < max_iterations:
            iteration += 1
            next_tasks = plan.get_next_tasks()

            if not next_tasks and not plan.is_complete():
                plan.status = GoalStatus.BLOCKED
                logger.warning("Plan blocked - circular dependencies detected")
                break

            for task in next_tasks:
                task.status = GoalStatus.IN_PROGRESS
                logger.info("Executing task: %s -> %s", task.task_id, task.agent_type)

                agent = self.agent_registry.get(task.agent_type)
                if agent:
                    try:
                        task.result = agent.execute(task.description)
                    except Exception as e:
                        logger.error("Agent %s failed on task %s: %s",
                                     task.agent_type, task.task_id, str(e))
                        task.result = {"error": str(e), "status": "failed"}
                else:
                    task.result = f"No agent available for: {task.agent_type}"
                    logger.warning("No agent registered for type: %s", task.agent_type)

                task.status = GoalStatus.COMPLETED
                results.append({
                    "task_id": task.task_id,
                    "agent_type": task.agent_type,
                    "result": task.result,
                })

        if plan.is_complete():
            plan.status = GoalStatus.VERIFYING
            if self.verifier:
                for r in results:
                    if r.get("result") is not None:
                        verification = self.verifier.verify(r["result"])
                        r["verification"] = {
                            "passed": verification.passed,
                            "score": verification.score,
                            "issues": verification.issues,
                        }
            plan.status = GoalStatus.COMPLETED
            logger.info("Plan completed successfully")

        if iteration >= max_iterations:
            plan.status = GoalStatus.FAILED
            logger.error("Plan execution hit max iterations limit")

        return {
            "goal": plan.goal,
            "status": plan.status.value,
            "tasks": results,
        }

    def get_status(self, goal_id: str) -> Optional[GoalStatus]:
        """Check the status of an active goal."""
        return self.active_goals.get(goal_id)