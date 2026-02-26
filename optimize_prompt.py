#!/usr/bin/env python3
"""
Main script to run DSPy COPRO optimization for conversation scoring

This script:
1. Loads conversation and scoring data
2. Splits into train/validation sets
3. Evaluates baseline performance
4. Runs COPRO optimization
5. Saves optimized module and results
"""
import json
import logging
from pathlib import Path
import litellm
import dspy

# Configure litellm to drop unsupported parameters for Ollama
litellm.drop_params = True

from src.config import (
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MAX_TOKENS,
    OLLAMA_TEMPERATURE,
    TRAIN_IDS,
    VAL_IDS,
    RESULTS_DIR
)
from src.data_loader import load_all_examples
from src.dspy_signatures import ConversationScoringModule
from src.metrics import evaluate_predictions
from src.optimizer import setup_copro_optimizer, run_optimization

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("DSPy COPRO Prompt Optimization")
    logger.info("=" * 60)
    logger.info("")

    # Step 1: Configure DSPy with Ollama
    logger.info("Step 1: Configuring DSPy with Ollama")
    logger.info(f"  Model: {OLLAMA_MODEL}")
    logger.info(f"  Base URL: {OLLAMA_BASE_URL}")
    logger.info(f"  Max tokens: {OLLAMA_MAX_TOKENS}")
    logger.info(f"  Temperature: {OLLAMA_TEMPERATURE}")
    logger.info("")

    lm = dspy.LM(
        model=f"ollama/{OLLAMA_MODEL}",
        api_base=OLLAMA_BASE_URL,
        max_tokens=OLLAMA_MAX_TOKENS,
        temperature=OLLAMA_TEMPERATURE
    )
    dspy.settings.configure(lm=lm)
    logger.info("✓ DSPy configured successfully")
    logger.info("")

    # Step 2: Load data
    logger.info("Step 2: Loading conversation data")
    logger.info(f"  Train IDs: {TRAIN_IDS}")
    logger.info(f"  Val IDs: {VAL_IDS}")
    logger.info("")

    train_examples = load_all_examples(TRAIN_IDS)
    val_examples = load_all_examples(VAL_IDS)

    logger.info(f"✓ Loaded {len(train_examples)} training examples")
    logger.info(f"✓ Loaded {len(val_examples)} validation examples")
    logger.info("")

    # Step 3: Create baseline module
    logger.info("Step 3: Creating baseline module")
    baseline_module = ConversationScoringModule()
    logger.info("✓ Baseline module created")
    logger.info("")

    # Step 4: Evaluate baseline
    logger.info("Step 4: Evaluating baseline performance")
    logger.info("  Testing on training set...")
    baseline_train_metrics = evaluate_predictions(train_examples, baseline_module)
    logger.info(f"  ✓ Train metrics: Score={baseline_train_metrics['avg_metric_score']:.2f}, "
                f"MAE={baseline_train_metrics['avg_mae']:.3f}, "
                f"Exact={baseline_train_metrics['avg_exact_matches']:.1f}")

    logger.info("  Testing on validation set...")
    baseline_val_metrics = evaluate_predictions(val_examples, baseline_module)
    logger.info(f"  ✓ Val metrics: Score={baseline_val_metrics['avg_metric_score']:.2f}, "
                f"MAE={baseline_val_metrics['avg_mae']:.3f}, "
                f"Exact={baseline_val_metrics['avg_exact_matches']:.1f}")
    logger.info("")

    # Save baseline results
    baseline_results = {
        "train": baseline_train_metrics,
        "validation": baseline_val_metrics
    }
    baseline_path = RESULTS_DIR / "baseline_results.json"
    with open(baseline_path, 'w') as f:
        json.dump(baseline_results, f, indent=2)
    logger.info(f"✓ Baseline results saved to {baseline_path}")
    logger.info("")

    # Step 5: Setup COPRO optimizer
    logger.info("Step 5: Setting up COPRO optimizer")
    optimizer = setup_copro_optimizer()
    logger.info("")

    # Step 6: Run optimization
    logger.info("Step 6: Running COPRO optimization")
    logger.info("  This will take approximately 30-60 minutes...")
    logger.info("  Progress will be logged as optimization proceeds")
    logger.info("")

    optimized_module = run_optimization(
        baseline_module,
        train_examples,
        val_examples,
        optimizer
    )
    logger.info("")

    # Step 7: Evaluate optimized module
    logger.info("Step 7: Evaluating optimized module")
    logger.info("  Testing on training set...")
    optimized_train_metrics = evaluate_predictions(train_examples, optimized_module)
    logger.info(f"  ✓ Train metrics: Score={optimized_train_metrics['avg_metric_score']:.2f}, "
                f"MAE={optimized_train_metrics['avg_mae']:.3f}, "
                f"Exact={optimized_train_metrics['avg_exact_matches']:.1f}")

    logger.info("  Testing on validation set...")
    optimized_val_metrics = evaluate_predictions(val_examples, optimized_module)
    logger.info(f"  ✓ Val metrics: Score={optimized_val_metrics['avg_metric_score']:.2f}, "
                f"MAE={optimized_val_metrics['avg_mae']:.3f}, "
                f"Exact={optimized_val_metrics['avg_exact_matches']:.1f}")
    logger.info("")

    # Save optimized results
    optimized_results = {
        "train": optimized_train_metrics,
        "validation": optimized_val_metrics
    }
    optimized_path = RESULTS_DIR / "optimized_results.json"
    with open(optimized_path, 'w') as f:
        json.dump(optimized_results, f, indent=2)
    logger.info(f"✓ Optimized results saved to {optimized_path}")
    logger.info("")

    # Step 8: Save optimized module
    logger.info("Step 8: Saving optimized module")
    module_dir = RESULTS_DIR / "optimized_module"
    module_dir.mkdir(exist_ok=True)
    module_path = module_dir / "program.json"
    optimized_module.save(str(module_path))
    logger.info(f"✓ Optimized module saved to {module_path}")
    logger.info("")

    # Step 9: Summary
    logger.info("=" * 60)
    logger.info("OPTIMIZATION SUMMARY")
    logger.info("=" * 60)

    # Calculate improvements
    train_improvement = (
        (optimized_train_metrics['avg_metric_score'] - baseline_train_metrics['avg_metric_score'])
        / baseline_train_metrics['avg_metric_score'] * 100
    )
    val_improvement = (
        (optimized_val_metrics['avg_metric_score'] - baseline_val_metrics['avg_metric_score'])
        / baseline_val_metrics['avg_metric_score'] * 100
    )

    logger.info(f"Baseline validation score: {baseline_val_metrics['avg_metric_score']:.2f}")
    logger.info(f"Optimized validation score: {optimized_val_metrics['avg_metric_score']:.2f}")
    logger.info(f"Improvement: {val_improvement:+.1f}%")
    logger.info("")
    logger.info(f"Baseline validation MAE: {baseline_val_metrics['avg_mae']:.3f}")
    logger.info(f"Optimized validation MAE: {optimized_val_metrics['avg_mae']:.3f}")
    logger.info("")

    # Save summary
    summary = {
        "baseline": baseline_results,
        "optimized": optimized_results,
        "improvement": {
            "train_percent": train_improvement,
            "validation_percent": val_improvement
        }
    }
    summary_path = RESULTS_DIR / "optimization_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"✓ Summary saved to {summary_path}")
    logger.info("")

    logger.info("=" * 60)
    logger.info("✓ OPTIMIZATION COMPLETE!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Review results in results/ directory")
    logger.info("  2. Run test_optimized.py to generate predictions")
    logger.info("  3. Compare baseline vs optimized performance")
    logger.info("")


if __name__ == "__main__":
    main()
