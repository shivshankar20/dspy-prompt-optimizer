"""Data loading utilities for conversation and scoring files"""
import re
from dataclasses import dataclass
from typing import Dict, List
import logging

from src.config import INPUTS_DIR, OUTPUT_DIR

logger = logging.getLogger(__name__)


@dataclass
class ConversationExample:
    """Data class for a conversation with its expected scores"""
    conversation: str
    expected_scores: Dict[str, int]
    expected_justifications: Dict[str, str]
    overall_score: int
    conversation_id: str


def load_conversation(conversation_id: int) -> str:
    """Load a conversation transcript from markdown file"""
    file_path = INPUTS_DIR / f"conversation_{conversation_id:02d}.md"
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_scoring_file(conversation_id: int) -> tuple[Dict[str, int], Dict[str, str], int]:
    """
    Parse a scoring markdown file to extract scores and justifications

    Returns:
        tuple: (scores_dict, justifications_dict, overall_score)
    """
    file_path = OUTPUT_DIR / f"scoring_{conversation_id:02d}.md"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    scores = {}
    justifications = {}

    # Extract dimension scores and justifications
    # Pattern: ### 1. Dimension Name: **X/5**
    score_pattern = r'### \d+\. ([^:]+): \*\*(\d+)/5\*\*'
    score_matches = re.findall(score_pattern, content)

    for dimension, score in score_matches:
        dimension = dimension.strip()
        scores[dimension] = int(score)

    # Extract justifications
    # Pattern: **Justification:** text (potentially multi-line until next ###)
    justification_pattern = r'\*\*Justification:\*\* ([^\n]+(?:\n(?!###|\*\*)[^\n]+)*)'
    justification_matches = re.findall(justification_pattern, content)

    # Map justifications to dimensions (same order as scores)
    for i, (dimension, _) in enumerate(score_matches):
        dimension = dimension.strip()
        if i < len(justification_matches):
            justifications[dimension] = justification_matches[i].strip()

    # Extract overall score
    # Pattern: ## Overall Score: **XX/25**
    overall_pattern = r'## Overall Score: \*\*(\d+)/25\*\*'
    overall_match = re.search(overall_pattern, content)
    overall_score = int(overall_match.group(1)) if overall_match else 0

    return scores, justifications, overall_score


def load_example(conversation_id: int) -> ConversationExample:
    """Load a single conversation example with its scoring"""
    conversation = load_conversation(conversation_id)
    scores, justifications, overall_score = parse_scoring_file(conversation_id)

    return ConversationExample(
        conversation=conversation,
        expected_scores=scores,
        expected_justifications=justifications,
        overall_score=overall_score,
        conversation_id=f"conversation_{conversation_id:02d}"
    )


def load_all_examples(conversation_ids: List[int]) -> List[ConversationExample]:
    """Load multiple conversation examples"""
    examples = []
    for conv_id in conversation_ids:
        try:
            example = load_example(conv_id)
            examples.append(example)
            logger.info(f"Loaded {example.conversation_id}")
        except Exception as e:
            logger.error(f"Failed to load conversation {conv_id}: {e}")

    logger.info(f"Total examples loaded: {len(examples)}")
    return examples
