#!/usr/bin/env python3
"""
Test script to generate predictions using the optimized module

This script:
1. Loads the optimized module
2. Generates predictions for all 10 conversations
3. Saves formatted outputs to results/test_outputs/
"""
import json
import logging
from typing import Union, Dict, Any
import litellm
import dspy

# Configure litellm to drop unsupported parameters for Ollama
litellm.drop_params = True

from src.config import (
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MAX_TOKENS,
    OLLAMA_TEMPERATURE,
    RESULTS_DIR,
    DIMENSIONS
)
from src.data_loader import load_all_examples
from src.dspy_signatures import ConversationScoringModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def format_scoring_output(conversation_id: str, prediction: Union[Dict[str, Any], Any]) -> str:
    """
    Format prediction results as markdown

    Args:
        conversation_id: ID of the conversation
        prediction: Dictionary or object with scores and justifications

    Returns:
        Formatted markdown string
    """
    # Handle both dict and object types
    if isinstance(prediction, dict):
        scores = prediction.get("scores", {})
        justifications = prediction.get("justifications", {})
    else:
        scores = getattr(prediction, "scores", {})
        justifications = getattr(prediction, "justifications", {})

    output = f"# Predicted Scoring - {conversation_id}\n\n"
    output += "## Dimension Scores\n\n"

    dimension_map = {
        "Professionalism and Courtesy": 1,
        "Problem Resolution": 2,
        "Empathy and Understanding": 3,
        "Communication Clarity": 4,
        "Efficiency and Effectiveness": 5
    }

    for dimension in DIMENSIONS:
        num = dimension_map.get(dimension, 0)
        score = scores.get(dimension, 0)
        justification = justifications.get(dimension, "N/A")

        output += f"### {num}. {dimension}: **{score}/5**\n"
        output += f"**Justification:** {justification}\n\n"

    # Calculate overall score
    overall_score = sum(scores.values())
    output += "---\n\n"
    output += f"## Overall Score: **{overall_score}/25**\n"

    return output


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Testing Optimized Module")
    logger.info("=" * 60)
    logger.info("")

    # Step 1: Configure DSPy
    logger.info("Step 1: Configuring DSPy with Ollama")
    lm = dspy.LM(
        model=f"ollama/{OLLAMA_MODEL}",
        api_base=OLLAMA_BASE_URL,
        max_tokens=OLLAMA_MAX_TOKENS,
        temperature=OLLAMA_TEMPERATURE
    )
    dspy.settings.configure(lm=lm)
    logger.info("✓ DSPy configured")
    logger.info("")

    # Step 2: Load optimized module
    logger.info("Step 2: Loading optimized module")
    module_dir = RESULTS_DIR / "optimized_module"
    module_path = module_dir / "program.json"

    if not module_path.exists():
        logger.error(f"Optimized module not found at {module_path}")
        logger.error("Please run optimize_prompt.py first!")
        return

    optimized_module = ConversationScoringModule()
    optimized_module.load(str(module_path))
    logger.info(f"✓ Loaded optimized module from {module_path}")
    logger.info("")

    # Step 3: Load all conversations
    logger.info("Step 3: Loading all conversations")
    all_ids = list(range(1, 11))  # 1 through 10
    all_examples = load_all_examples(all_ids)
    logger.info(f"✓ Loaded {len(all_examples)} conversations")
    logger.info("")

    # Step 4: Generate predictions
    logger.info("Step 4: Generating predictions")
    output_dir = RESULTS_DIR / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    predictions_data = {}

    for example in all_examples:
        logger.info(f"  Processing {example.conversation_id}...")

        # Generate prediction
        prediction = optimized_module(conversation=example.conversation)

        # Format and save output
        formatted_output = format_scoring_output(example.conversation_id, prediction)
        output_path = output_dir / f"{example.conversation_id}_predicted.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_output)

        logger.info(f"    ✓ Saved to {output_path}")

        # Store for JSON summary
        if isinstance(prediction, dict):
            predictions_data[example.conversation_id] = {
                "scores": prediction.get("scores", {}),
                "justifications": prediction.get("justifications", {})
            }
        else:
            predictions_data[example.conversation_id] = {
                "scores": getattr(prediction, "scores", {}),
                "justifications": getattr(prediction, "justifications", {})
            }

    logger.info("")

    # Step 5: Save JSON summary
    logger.info("Step 5: Saving predictions summary")
    summary_path = RESULTS_DIR / "predictions_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(predictions_data, f, indent=2)
    logger.info(f"✓ Summary saved to {summary_path}")
    logger.info("")

    logger.info("=" * 60)
    logger.info("✓ TESTING COMPLETE!")
    logger.info("=" * 60)
    logger.info("")
    logger.info(f"Results saved to: {output_dir}")
    logger.info(f"  - {len(all_examples)} markdown files with predictions")
    logger.info(f"  - JSON summary at {summary_path}")
    logger.info("")


if __name__ == "__main__":
    main()
