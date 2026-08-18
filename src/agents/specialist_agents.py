"""
Specialist Agents - Research, Analyst, Writer, Developer, Executive Assistant.

Each agent uses the shared LLM client to actually perform its designated task,
rather than returning placeholder status messages.
"""

import logging
from typing import Optional

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Specialist agent for research tasks.

    Capabilities:
    - Web research and information gathering
    - Fact-checking and source verification
    - Evidence-backed findings
    - Topic summarization
    """

    SYSTEM_PROMPT = (
        "You are a Research Agent in the AI Work OS. Your job is to research "
        "the given topic thoroughly. Gather evidence, cite sources when "
        "possible, and produce a clear, well-structured summary of findings. "
        "Always prioritise accuracy and evidence."
    )

    def __init__(self, llm=None):
        super().__init__(
            name="Research",
            description="Researches information and produces evidence-backed findings",
            llm=llm,
        )
        self.capabilities = [
            "web_research",
            "fact_checking",
            "source_verification",
            "summarization",
        ]

    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """Execute a research task.

        Args:
            task: Research question or topic.
            context: Optional context (preferred sources, depth, etc.).

        Returns:
            Research findings with sources.
        """
        prompt = f"Research the following topic thoroughly:\n\n{task}"
        if context and "preferred_sources" in context:
            prompt += f"\n\nPreferred sources: {context['preferred_sources']}"

        content = self._llm_call(prompt, temperature=0.3)

        return self._build_result(
            task=task,
            content=content,
            extra={
                "agent": "research",
                "sources": [],
                "findings": content,
            },
        )


class AnalystAgent(BaseAgent):
    """Specialist agent for analysis tasks.

    Capabilities:
    - Data analysis and interpretation
    - Trend identification
    - Business analysis
    - Report generation
    """

    SYSTEM_PROMPT = (
        "You are an Analyst Agent in the AI Work OS. Your job is to analyse "
        "data, identify trends, and generate insightful business analysis. "
        "Structure your response with clear sections for key findings, "
        "data interpretation, and actionable recommendations."
    )

    def __init__(self, llm=None):
        super().__init__(
            name="Analyst",
            description="Analyses datasets, trends and business information",
            llm=llm,
        )
        self.capabilities = [
            "data_analysis",
            "trend_analysis",
            "business_analysis",
            "report_generation",
        ]

    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """Execute an analysis task using LLM-powered analysis."""
        prompt = f"Analyze the following:\n\n{task}"
        if context and "data" in context:
            prompt += f"\n\nData:\n{context['data']}"

        content = self._llm_call(prompt, temperature=0.4)
        return self._build_result(
            task=task, content=content, extra={"agent": "analyst", "analysis": content}
        )


class WriterAgent(BaseAgent):
    """Specialist agent for writing tasks.

    Capabilities:
    - Report and proposal writing
    - Email composition
    - Document creation
    - Content editing
    """

    SYSTEM_PROMPT = (
        "You are a Writer Agent in the AI Work OS. Your job is to create "
        "well-structured, professional content. Whether it's reports, proposals, "
        "emails, or documents, you produce clear, engaging, and polished "
        "writing tailored to the audience and purpose."
    )

    def __init__(self, llm=None):
        super().__init__(
            name="Writer",
            description="Creates reports, proposals, emails and documents",
            llm=llm,
        )
        self.capabilities = [
            "report_writing",
            "proposal_writing",
            "email_composition",
            "document_creation",
            "editing",
        ]

    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """Execute a writing task using LLM-powered content generation."""
        prompt = f"Write the following:\n\n{task}"
        if context and "style" in context:
            prompt += f"\n\nWriting style: {context['style']}"
        if context and "audience" in context:
            prompt += f"\nAudience: {context['audience']}"
        if context and "content" in context:
            prompt += f"\n\nReference material:\n{context['content']}"

        content = self._llm_call(prompt, temperature=0.7)
        return self._build_result(
            task=task, content=content, extra={"agent": "writer", "draft": content}
        )


class DeveloperAgent(BaseAgent):
    """Specialist agent for development tasks.

    Capabilities:
    - Code generation and review
    - Repository management
    - Bug fixing
    - Technical documentation
    """

    SYSTEM_PROMPT = (
        "You are a Developer Agent in the AI Work OS. Your job is to "
        "write, review, and debug code. Produce clean, well-documented, "
        "production-ready code. When generating code, include explanatory "
        "comments. When reviewing, focus on correctness, readability, "
        "and best practices."
    )

    def __init__(self, llm=None):
        super().__init__(
            name="Developer",
            description="Works with code, repositories and development tools",
            llm=llm,
        )
        self.capabilities = [
            "code_generation",
            "code_review",
            "debugging",
            "documentation",
        ]

    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """Execute a development task using LLM-powered code generation."""
        prompt = f"As a developer, complete the following task:\n\n{task}"
        if context and "language" in context:
            prompt += f"\n\nProgramming language: {context['language']}"
        if context and "codebase_context" in context:
            prompt += f"\n\nCodebase context:\n{context['codebase_context']}"
        if context and "code" in context:
            prompt += f"\n\nExisting code:\n```\n{context['code']}\n```"

        content = self._llm_call(prompt, temperature=0.3)
        return self._build_result(
            task=task, content=content, extra={"agent": "developer", "output": content}
        )


class ExecutiveAssistantAgent(BaseAgent):
    """Specialist agent for executive assistance.

    Capabilities:
    - Meeting management and preparation
    - Schedule coordination
    - Task prioritization
    - Briefing preparation
    """

    SYSTEM_PROMPT = (
        "You are an Executive Assistant Agent in the AI Work OS. Your job is "
        "to manage meetings, schedules, and prepare briefings. You help "
        "executives stay organized, prioritise tasks effectively, and "
        "prepare concise, informative materials for meetings and presentations."
    )

    def __init__(self, llm=None):
        super().__init__(
            name="Executive Assistant",
            description="Manages meetings, schedules and preparation",
            llm=llm,
        )
        self.capabilities = [
            "meeting_management",
            "schedule_coordination",
            "task_prioritization",
            "briefing_preparation",
        ]

    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """Execute an executive assistance task using LLM-powered planning."""
        prompt = f"As an executive assistant, complete the following task:\n\n{task}"
        if context and "agenda" in context:
            prompt += f"\n\nAgenda: {context['agenda']}"
        if context and "participants" in context:
            prompt += f"\n\nParticipants: {context['participants']}"
        if context and "deadline" in context:
            prompt += f"\nDeadline: {context['deadline']}"

        content = self._llm_call(prompt, temperature=0.5)
        return self._build_result(
            task=task, content=content,
            extra={"agent": "executive_assistant", "result": content}
        )