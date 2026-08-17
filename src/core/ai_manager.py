"""
AI Manager - The central orchestrator of the AI Work OS.

The Manager Agent receives user goals, creates plans,
and coordinates specialist agents to accomplish work.
"""

from typing import List, Optional
from enum import Enum


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

    def __init__(self):
        self.active_goals: dict = {}
        self.agent_registry = {}

    def register_agent(self, agent_type: str, agent_instance):
        """Register a specialist agent with the manager."""
        self.agent_registry[agent_type] = agent_instance

    def create_plan(self, goal: str) -> Plan:
        """
        Analyze a user goal and create an execution plan.

        In the full implementation, this would use an AI model
        to decompose the goal into tasks and assign agents.
        """
        plan = Plan(goal=goal)
        plan.status = GoalStatus.PLANNING
        return plan

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