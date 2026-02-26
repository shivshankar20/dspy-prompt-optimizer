"""DSPy signatures and modules for conversation scoring"""
import re
from typing import Dict
import dspy

from src.config import DIMENSIONS


class ConversationScoring(dspy.Signature):
    """Evaluate customer service conversation using this scoring rubric. Each dimension is scored 1-5.

## 1. Professionalism and Courtesy
Definition: Agent's demeanor, politeness, and professional behavior throughout the interaction.
- 5 (Excellent): Agent is consistently polite, uses professional language, maintains positive tone even when customer is upset, personalizes interaction appropriately
- 4 (Good): Agent is polite and professional throughout, minor lapses in tone or formality
- 3 (Satisfactory): Agent is generally professional but may sound scripted or occasionally dismissive
- 2 (Needs Improvement): Agent shows impatience, uses inappropriate casual language, or lacks warmth
- 1 (Poor): Agent is rude, dismissive, or unprofessional

## 2. Problem Resolution
Definition: Effectiveness and completeness of the solution provided to the customer's issue.
- 5 (Excellent): Issue completely resolved, additional value provided (proactive suggestions, alternatives, compensation when appropriate), customer satisfaction confirmed
- 4 (Good): Issue resolved satisfactorily, customer's needs met, clear next steps provided
- 3 (Satisfactory): Partial resolution or workaround provided, some aspects of the issue remain unaddressed
- 2 (Needs Improvement): Minimal progress on resolution, customer left with uncertainty or additional steps required
- 1 (Poor): Issue unresolved, no viable solution offered, or incorrect information provided

## 3. Empathy and Understanding
Definition: Ability to acknowledge customer emotions, show understanding, and respond with appropriate empathy.
- 5 (Excellent): Agent actively acknowledges customer's feelings, validates concerns, shows genuine understanding, and adjusts approach based on customer's emotional state
- 4 (Good): Agent recognizes customer emotions and responds with empathy, makes customer feel heard
- 3 (Satisfactory): Agent acknowledges the issue but shows limited emotional engagement or empathy
- 2 (Needs Improvement): Agent appears indifferent to customer's concerns or frustration
- 1 (Poor): Agent dismisses or ignores customer's emotional state, lacks any empathy

## 4. Communication Clarity
Definition: How clearly and effectively the agent explains information, processes, and solutions.
- 5 (Excellent): Information presented in clear, simple language; complex concepts explained well; agent confirms understanding; no jargon or ambiguity
- 4 (Good): Clear communication with minor opportunities for improvement; agent mostly checks for understanding
- 3 (Satisfactory): Generally understandable but may include some confusing explanations or missed opportunities to clarify
- 2 (Needs Improvement): Explanations are unclear, overly technical, or confusing; agent doesn't verify understanding
- 1 (Poor): Communication is confusing, contradictory, or incomprehensible

## 5. Efficiency and Effectiveness
Definition: How quickly and efficiently the agent handles the interaction without sacrificing quality.
- 5 (Excellent): Agent resolves issue quickly, takes ownership, minimizes customer effort, proactively gathers needed information, no unnecessary delays
- 4 (Good): Efficient handling with minor delays; agent stays on topic and moves toward resolution
- 3 (Satisfactory): Adequate pacing but may include unnecessary steps or slightly prolonged interaction
- 2 (Needs Improvement): Slow progress, excessive back-and-forth, or failure to gather necessary information efficiently
- 1 (Poor): Significant delays, agent appears lost or unsure, wastes customer's time

For each dimension, provide the score (1-5) and a clear justification referencing the rubric criteria."""

    conversation = dspy.InputField(desc="The full customer service conversation transcript")

    # Output fields for each dimension (5 dimensions × 2 fields each = 10 fields)
    professionalism_score = dspy.OutputField(desc="Score for Professionalism and Courtesy (1-5)")
    professionalism_justification = dspy.OutputField(desc="Justification for Professionalism score")

    problem_resolution_score = dspy.OutputField(desc="Score for Problem Resolution (1-5)")
    problem_resolution_justification = dspy.OutputField(desc="Justification for Problem Resolution score")

    empathy_score = dspy.OutputField(desc="Score for Empathy and Understanding (1-5)")
    empathy_justification = dspy.OutputField(desc="Justification for Empathy score")

    communication_score = dspy.OutputField(desc="Score for Communication Clarity (1-5)")
    communication_justification = dspy.OutputField(desc="Justification for Communication score")

    efficiency_score = dspy.OutputField(desc="Score for Efficiency and Effectiveness (1-5)")
    efficiency_justification = dspy.OutputField(desc="Justification for Efficiency score")


class ConversationScoringModule(dspy.Module):
    """Module for scoring customer service conversations"""

    def __init__(self):
        super().__init__()
        self.scorer = dspy.ChainOfThought(ConversationScoring)

    def forward(self, conversation: str) -> Dict:
        """
        Score a conversation and return structured results

        Args:
            conversation: The conversation transcript

        Returns:
            Dict with scores and justifications for each dimension
        """
        result = self.scorer(conversation=conversation)

        # Parse scores from the result
        scores = {
            "Professionalism and Courtesy": self._parse_score(result.professionalism_score),
            "Problem Resolution": self._parse_score(result.problem_resolution_score),
            "Empathy and Understanding": self._parse_score(result.empathy_score),
            "Communication Clarity": self._parse_score(result.communication_score),
            "Efficiency and Effectiveness": self._parse_score(result.efficiency_score),
        }

        justifications = {
            "Professionalism and Courtesy": result.professionalism_justification,
            "Problem Resolution": result.problem_resolution_justification,
            "Empathy and Understanding": result.empathy_justification,
            "Communication Clarity": result.communication_justification,
            "Efficiency and Effectiveness": result.efficiency_justification,
        }

        return {
            "scores": scores,
            "justifications": justifications
        }

    @staticmethod
    def _parse_score(score_text: str) -> int:
        """
        Extract numeric score from text output

        Args:
            score_text: Text that may contain a score

        Returns:
            Integer score (1-5), defaults to 3 if parsing fails
        """
        # Try to extract a number from the text
        match = re.search(r'\b([1-5])\b', str(score_text))
        if match:
            return int(match.group(1))

        # Default to middle score if parsing fails
        return 3
