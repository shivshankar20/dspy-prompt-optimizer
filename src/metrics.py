"""Metrics for evaluating conversation scoring predictions"""
import logging
from typing import Dict
import dspy

from src.data_loader import ConversationExample
from src.config import DIMENSIONS

logger = logging.getLogger(__name__)


def scoring_metric(example: ConversationExample, prediction, trace=None) -> float:
    """
    Composite metric for evaluating scoring predictions

    Scoring rubric:
    - Start at 100 points
    - Deduct 10 points per MAE unit across dimensions
    - Add 5 points per exact match
    - Deduct points for overall score error

    Args:
        example: The ground truth example
        prediction: The predicted scores
        trace: Optional trace (unused)

    Returns:
        Score between 0-100+ (higher is better)
    """
    try:
        # Extract predicted scores
        predicted_scores = prediction.get("scores", {})

        # Calculate MAE across dimensions
        total_absolute_error = 0
        exact_matches = 0
        scored_dimensions = 0

        for dimension in DIMENSIONS:
            if dimension in example.expected_scores and dimension in predicted_scores:
                expected = example.expected_scores[dimension]
                predicted = predicted_scores[dimension]

                # Absolute error
                error = abs(expected - predicted)
                total_absolute_error += error

                # Exact match bonus
                if error == 0:
                    exact_matches += 1

                scored_dimensions += 1

        # Calculate MAE
        mae = total_absolute_error / max(scored_dimensions, 1)

        # Start with base score
        score = 100.0

        # Deduct for MAE (10 points per unit)
        score -= mae * 10

        # Add bonus for exact matches (5 points each)
        score += exact_matches * 5

        # Calculate overall score error (sum of all dimension scores)
        predicted_overall = sum(predicted_scores.values())
        expected_overall = example.overall_score
        overall_error = abs(predicted_overall - expected_overall)

        # Deduct for overall score error (2 points per unit)
        score -= overall_error * 2

        # Ensure score is non-negative
        score = max(0.0, score)

        logger.debug(
            f"Metric for {example.conversation_id}: "
            f"MAE={mae:.2f}, Exact={exact_matches}, "
            f"Overall_Error={overall_error}, Score={score:.2f}"
        )

        return score

    except Exception as e:
        logger.error(f"Error calculating metric: {e}")
        return 0.0


def evaluate_predictions(examples, module) -> Dict:
    """
    Evaluate module on a set of examples

    Args:
        examples: List of ConversationExample objects
        module: The DSPy module to evaluate

    Returns:
        Dictionary with evaluation metrics
    """
    total_score = 0.0
    total_mae = 0.0
    total_exact = 0
    num_examples = len(examples)

    for example in examples:
        # Get prediction
        prediction = module(conversation=example.conversation)

        # Calculate metric
        metric_score = scoring_metric(example, prediction)
        total_score += metric_score

        # Calculate MAE for this example
        predicted_scores = prediction.get("scores", {})
        mae_sum = 0
        exact_matches = 0

        for dimension in DIMENSIONS:
            if dimension in example.expected_scores and dimension in predicted_scores:
                expected = example.expected_scores[dimension]
                predicted = predicted_scores[dimension]
                mae_sum += abs(expected - predicted)

                if expected == predicted:
                    exact_matches += 1

        total_mae += mae_sum / len(DIMENSIONS)
        total_exact += exact_matches

    avg_score = total_score / max(num_examples, 1)
    avg_mae = total_mae / max(num_examples, 1)
    avg_exact = total_exact / max(num_examples, 1)

    return {
        "avg_metric_score": avg_score,
        "avg_mae": avg_mae,
        "avg_exact_matches": avg_exact,
        "num_examples": num_examples
    }
