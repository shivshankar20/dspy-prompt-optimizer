"""COPRO optimizer setup and execution"""
import logging
from typing import List
import dspy
from dspy.teleprompt import COPRO

from src.config import (
    COPRO_BREADTH,
    COPRO_DEPTH,
    COPRO_INIT_TEMP,
    COPRO_NUM_THREADS
)
from src.data_loader import ConversationExample
from src.metrics import scoring_metric

logger = logging.getLogger(__name__)


def setup_copro_optimizer() -> COPRO:
    """
    Create and configure COPRO optimizer

    Returns:
        Configured COPRO optimizer instance
    """
    logger.info("Setting up COPRO optimizer")
    logger.info(f"  Breadth: {COPRO_BREADTH} prompt variants per iteration")
    logger.info(f"  Depth: {COPRO_DEPTH} optimization rounds")
    logger.info(f"  Init temperature: {COPRO_INIT_TEMP}")
    logger.info(f"  Num threads: {COPRO_NUM_THREADS}")

    optimizer = COPRO(
        metric=scoring_metric,
        breadth=COPRO_BREADTH,
        depth=COPRO_DEPTH,
        init_temperature=COPRO_INIT_TEMP,
        num_threads=COPRO_NUM_THREADS
    )

    return optimizer


def run_optimization(
    module,
    train_examples: List[ConversationExample],
    val_examples: List[ConversationExample],
    optimizer: COPRO
):
    """
    Run COPRO optimization on the module

    Args:
        module: The DSPy module to optimize
        train_examples: Training examples
        val_examples: Validation examples
        optimizer: The COPRO optimizer

    Returns:
        Optimized module
    """
    logger.info("=" * 60)
    logger.info("Starting COPRO optimization")
    logger.info("=" * 60)
    logger.info(f"Training examples: {len(train_examples)}")
    logger.info(f"Validation examples: {len(val_examples)}")
    logger.info("")

    # Convert examples to dspy.Example format
    train_set = []
    for ex in train_examples:
        # Create dspy.Example with conversation as input
        dspy_ex = dspy.Example(
            conversation=ex.conversation,
            # Store the full example for metric calculation
            _example_data=ex
        ).with_inputs("conversation")
        train_set.append(dspy_ex)

    val_set = []
    for ex in val_examples:
        dspy_ex = dspy.Example(
            conversation=ex.conversation,
            _example_data=ex
        ).with_inputs("conversation")
        val_set.append(dspy_ex)

    # Custom metric wrapper to handle dspy.Example format
    def copro_metric(example, prediction, trace=None):
        # Extract the original ConversationExample
        original_example = example._example_data
        return scoring_metric(original_example, prediction, trace)

    # Update optimizer metric
    optimizer.metric = copro_metric

    logger.info("Running COPRO optimization (this may take 30-60 minutes)...")
    logger.info("")

    try:
        # Combine train and val sets for COPRO optimization
        # COPRO uses cross-validation internally
        all_examples = train_set + val_set

        optimized_module = optimizer.compile(
            module,
            trainset=all_examples,
            eval_kwargs={"num_threads": COPRO_NUM_THREADS}
        )

        logger.info("")
        logger.info("=" * 60)
        logger.info("COPRO optimization completed successfully!")
        logger.info("=" * 60)

        return optimized_module

    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise
