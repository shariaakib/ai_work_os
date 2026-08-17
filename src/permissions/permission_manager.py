"""
Permission Manager - Safety and approval system for AI actions.

Three permission levels:
🟢 Safe — AI can do automatically (read, search, analyse, draft)
🟡 Approval — AI asks before executing (send email, modify calendar)
🔴 High risk — Always require confirmation (transactions, deletion, security)
"""

from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass


class PermissionLevel(Enum):
    SAFE = "safe"
    APPROVAL = "approval"
    HIGH_RISK = "high_risk"


@dataclass
class Action:
    """An action that requires permission checking."""

    action_type: str
    description: str
    level: PermissionLevel
    requires_approval: bool = False
    is_approved: bool = False


class PermissionManager:
    """
    Manages permissions and safety for AI actions.

    Usage:
        pm = PermissionManager()
        action = Action("send_email", "Send proposal to client", PermissionLevel.APPROVAL)
        if pm.can_execute(action):
            pm.execute(action)
        else:
            pm.request_approval(action)
    """

    def __init__(self):
        self.pending_approvals: list[Action] = []
        self.approval_callback: Optional[Callable] = None
        self.auto_approve_safe = True

    def classify_action(self, action_type: str, description: str) -> PermissionLevel:
        """
        Classify an action into a permission level.

        Safe actions: read, search, analyse, summarise, draft
        Approval actions: send, modify, create, update, delete (non-critical)
        High risk actions: financial, irreversible_delete, security, legal
        """
        action_lower = action_type.lower()

        # Safe actions
        if action_lower in ["read", "search", "analyse", "analyze", "summarise",
                            "summarize", "draft", "list", "get", "find", "check"]:
            return PermissionLevel.SAFE

        # High risk actions
        if action_lower in ["payment", "transfer", "delete", "remove", "terminate",
                            "security_change", "legal_action", "irreversible"]:
            return PermissionLevel.HIGH_RISK

        # Everything else requires approval
        return PermissionLevel.APPROVAL

    def can_execute(self, action: Action) -> bool:
        """Check if an action can be executed without approval."""
        if action.level == PermissionLevel.SAFE and self.auto_approve_safe:
            return True
        if action.is_approved:
            return True
        return False

    def request_approval(self, action: Action) -> bool:
        """
        Request human approval for an action.

        In full implementation, this would send a notification
        to the user and wait for response.
        """
        action.requires_approval = True
        self.pending_approvals.append(action)
        if self.approval_callback:
            self.approval_callback(action)
        return False

    def approve(self, action: Action) -> bool:
        """Approve a pending action."""
        if action in self.pending_approvals:
            action.is_approved = True
            self.pending_approvals.remove(action)
            return True
        return False

    def reject(self, action: Action) -> bool:
        """Reject a pending action."""
        if action in self.pending_approvals:
            self.pending_approvals.remove(action)
            return True
        return False

    def get_pending_approvals(self) -> list[Action]:
        """Get list of actions waiting for approval."""
        return self.pending_approvals.copy()

    def set_approval_callback(self, callback: Callable):
        """Set a callback for when approval is needed."""
        self.approval_callback = callback