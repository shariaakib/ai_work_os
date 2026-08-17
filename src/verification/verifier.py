"""
Verifier - Ensures AI outputs are accurate, safe, and reliable.

Verification steps:
1. Check output completeness
2. Validate against requirements
3. Check for errors or inconsistencies
4. Auto-fix minor issues when confidence is high
"""

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class VerificationResult:
    """Result of a verification check."""

    passed: bool
    score: float  # 0.0 to 1.0
    issues: list[str]
    suggestions: list[str]


class Verifier:
    """
    Verifies AI outputs for accuracy and completeness.

    Usage:
        verifier = Verifier()
        result = verifier.verify(output, requirements)
        if result.passed:
            print("Output verified!")
    """

    def __init__(self, auto_fix_threshold: float = 0.8):
        self.auto_fix_threshold = auto_fix_threshold

    def verify(self, output: Any, requirements: Optional[dict] = None) -> VerificationResult:
        """
        Verify an AI output.

        Args:
            output: The output to verify
            requirements: Expected requirements or criteria

        Returns:
            VerificationResult with pass/fail, score, and issues
        """
        issues = []
        suggestions = []

        # Check if output exists
        if output is None:
            issues.append("Output is empty")
            return VerificationResult(False, 0.0, issues, ["Generate the output again"])

        # Check for common error patterns
        if isinstance(output, str):
            if "error" in output.lower():
                issues.append("Output contains error indicators")
                suggestions.append("Review and fix the error")
            if output.strip() == "":
                issues.append("Output is empty string")
                suggestions.append("Regenerate content")

        # Check requirements
        if requirements:
            for key, value in requirements.items():
                if isinstance(output, dict) and key not in output:
                    issues.append(f"Missing required field: {key}")
                    suggestions.append(f"Add {key} to the output")

        # Calculate score
        if len(issues) == 0:
            score = 1.0
        else:
            score = max(0.0, 1.0 - (len(issues) * 0.2))

        return VerificationResult(
            passed=score >= self.auto_fix_threshold,
            score=score,
            issues=issues,
            suggestions=suggestions,
        )

    def can_auto_fix(self, result: VerificationResult) -> bool:
        """Check if issues can be automatically fixed."""
        return result.score >= self.auto_fix_threshold and len(result.issues) > 0

    def suggest_fix(self, result: VerificationResult) -> str:
        """Get a suggested fix for verification issues."""
        if result.suggestions:
            return result.suggestions[0]
        return "Manual review required"