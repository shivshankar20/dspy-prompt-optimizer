#!/usr/bin/env python3
"""
Extract optimized prompts from DSPy COPRO optimization results

This script:
1. Loads the optimized module from results/optimized_module/
2. Extracts prompts from the signature (main instructions + field-level prompts)
3. Formats them as markdown and saves to OPTIMIZED-SYSTEM-PROMPT.md
4. Creates clean API-ready prompt and saves to OPTIMIZED-PROMPT.txt
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
    RESULTS_DIR,
    DIMENSIONS
)
from src.dspy_signatures import ConversationScoringModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_signature_prompts(module: ConversationScoringModule) -> dict:
    """
    Extract prompts from the optimized module's signature

    Args:
        module: The optimized ConversationScoringModule

    Returns:
        Dict containing main instructions and field-level prompts
    """
    # Get the ChainOfThought predictor and access the inner Predict module
    # COPRO optimizes the signature stored in predictor.predict
    predictor = module.scorer

    # Access the optimized signature from the predict module
    if hasattr(predictor, 'predict') and hasattr(predictor.predict, 'signature'):
        signature = predictor.predict.signature
    elif hasattr(predictor, 'signature'):
        signature = predictor.signature
    else:
        # Fallback to the base signature class
        from src.dspy_signatures import ConversationScoring
        signature = ConversationScoring

    # Extract main instructions (COPRO optimizes this!)
    main_instructions = getattr(signature, 'instructions',
                                getattr(signature, '__doc__',
                                       'Evaluate a customer service conversation across multiple dimensions'))

    # Extract field-level prompts
    field_prompts = {}

    # Get all output fields from the signature
    if hasattr(signature, 'model_fields'):
        for field_name, field_info in signature.model_fields.items():
            if field_name == 'conversation':  # Skip input field
                continue

            # Extract field description
            description = field_info.description if hasattr(field_info, 'description') else ''

            # Extract prefix from json_schema_extra
            prefix = ''
            if hasattr(field_info, 'json_schema_extra') and field_info.json_schema_extra:
                prefix = field_info.json_schema_extra.get('prefix', '')
                # Also get desc from json_schema_extra if available
                if not description:
                    description = field_info.json_schema_extra.get('desc', '')

            field_prompts[field_name] = {
                'description': description,
                'prefix': prefix
            }

    return {
        'main_instructions': main_instructions,
        'field_prompts': field_prompts
    }


def format_as_markdown(prompts: dict, summary: dict) -> str:
    """
    Format extracted prompts as markdown

    Args:
        prompts: Dict with main_instructions and field_prompts
        summary: Performance summary from optimization_summary.json

    Returns:
        Formatted markdown string
    """
    baseline_val = summary['baseline']['validation']
    optimized_val = summary['optimized']['validation']
    improvement_pct = summary['improvement']['validation_percent']

    baseline_train = summary['baseline']['train']
    optimized_train = summary['optimized']['train']
    train_improvement_pct = summary['improvement']['train_percent']

    md = f"""# Optimized System Prompt - DSPy COPRO Results

## Performance Improvement

### Validation Set (2 examples)
- **Baseline Score:** {baseline_val['avg_metric_score']:.2f}
- **Optimized Score:** {optimized_val['avg_metric_score']:.2f}
- **Improvement:** {improvement_pct:+.1f}%
- **Mean Absolute Error:** {baseline_val['avg_mae']:.3f} → {optimized_val['avg_mae']:.3f}
- **Exact Matches:** {baseline_val['avg_exact_matches']:.1f} → {optimized_val['avg_exact_matches']:.1f}

### Training Set (8 examples)
- **Baseline Score:** {baseline_train['avg_metric_score']:.2f}
- **Optimized Score:** {optimized_train['avg_metric_score']:.2f}
- **Improvement:** {train_improvement_pct:+.1f}%
- **Mean Absolute Error:** {baseline_train['avg_mae']:.3f} → {optimized_train['avg_mae']:.3f}
- **Exact Matches:** {baseline_train['avg_exact_matches']:.1f} → {optimized_train['avg_exact_matches']:.1f}

## Main System Instruction (COPRO Optimized)

COPRO optimized the main instruction to be more comprehensive and detailed:

```
{prompts['main_instructions']}
```

**Original Baseline:**
```
Evaluate a customer service conversation across multiple dimensions
```

## Field-Level Prompts

The optimized module uses the following field-level prompts for structured output:

"""

    # Group fields by dimension
    dimensions_map = {
        'professionalism': 'Professionalism and Courtesy',
        'problem_resolution': 'Problem Resolution',
        'empathy': 'Empathy and Understanding',
        'communication': 'Communication Clarity',
        'efficiency': 'Efficiency and Effectiveness'
    }

    # Special handling for reasoning field
    if 'reasoning' in prompts['field_prompts']:
        md += f"\n### Chain-of-Thought Reasoning\n\n"
        field_data = prompts['field_prompts']['reasoning']
        md += f"**Field:** `reasoning`\n\n"
        if field_data['prefix']:
            md += f"- **Prefix:** {field_data['prefix']}\n"
        if field_data['description']:
            md += f"- **Description:** {field_data['description']}\n"
        md += "\n"

    for field_prefix, dimension_name in dimensions_map.items():
        md += f"\n### {dimension_name}\n\n"

        # Score field
        score_field = f"{field_prefix}_score"
        if score_field in prompts['field_prompts']:
            field_data = prompts['field_prompts'][score_field]
            md += f"**Score Field:** `{score_field}`\n\n"
            if field_data['prefix']:
                md += f"- **Prefix:** `{field_data['prefix']}`\n"
            if field_data['description']:
                md += f"- **Description:** {field_data['description']}\n"
            md += "\n"

        # Justification field
        just_field = f"{field_prefix}_justification"
        if just_field in prompts['field_prompts']:
            field_data = prompts['field_prompts'][just_field]
            md += f"**Justification Field:** `{just_field}`\n\n"
            if field_data['prefix']:
                # Check if this is an optimized prefix (longer than standard)
                is_optimized = len(field_data['prefix']) > 50
                if is_optimized:
                    md += f"- **Prefix (COPRO Optimized):**\n  > {field_data['prefix']}\n"
                else:
                    md += f"- **Prefix:** `{field_data['prefix']}`\n"
            if field_data['description']:
                md += f"- **Description:** {field_data['description']}\n"
            md += "\n"

    md += """
## Usage

To use these optimized prompts in production:

1. **System Prompt:** Copy the main instruction as your system prompt
2. **Field Structure:** Use the field-level prompts to structure your output requests
3. **Scoring Dimensions:** Maintain the 5-dimension scoring structure (1-5 scale)
4. **Justifications:** Request justifications for each score to ensure transparency

## Implementation Example

```python
import dspy
from src.dspy_signatures import ConversationScoringModule

# Load the optimized module
module = ConversationScoringModule()
module.load("results/optimized_module/")

# Score a conversation
result = module(conversation=conversation_text)
print(result['scores'])
print(result['justifications'])
```

## Optimization Details

- **Optimizer:** DSPy COPRO (Prompt Optimization)
- **Training Examples:** 8 conversations
- **Validation Examples:** 2 conversations
- **Optimization Rounds:** 3 depth × 10 breadth = 30 iterations
- **Model:** llama3
- **Temperature:** 0.0

## Notes

- These prompts were automatically optimized using DSPy's COPRO algorithm
- The optimization focused on improving scoring accuracy and reducing MAE
- Performance metrics are based on validation set evaluation
- For best results, use with the same model configuration used during optimization
"""

    return md


def create_clean_prompt(prompts: dict) -> str:
    """
    Create clean API-ready prompt text (no DSPy, no documentation)

    Args:
        prompts: Dict with main_instructions and field_prompts

    Returns:
        Clean prompt text ready for any LLM API
    """
    # Start with main instruction
    prompt = prompts['main_instructions'] + "\n\n"

    # Check if efficiency_justification has an optimized prefix
    efficiency_prefix = ""
    if 'efficiency_justification' in prompts['field_prompts']:
        eff_prefix = prompts['field_prompts']['efficiency_justification'].get('prefix', '')
        # If it's a long optimized prefix (not just "Efficiency Justification:")
        if len(eff_prefix) > 50:
            efficiency_prefix = eff_prefix
            prompt += efficiency_prefix + "\n\n"

    # Add output structure
    prompt += "Provide scores (1-5) and justifications for the following dimensions:\n\n"

    # Add dimensions
    dimensions_map = {
        'professionalism': 'Professionalism and Courtesy',
        'problem_resolution': 'Problem Resolution',
        'empathy': 'Empathy and Understanding',
        'communication': 'Communication Clarity',
        'efficiency': 'Efficiency and Effectiveness'
    }

    for i, (field_prefix, dimension_name) in enumerate(dimensions_map.items(), 1):
        prompt += f"{i}. {dimension_name}\n"
        prompt += f"   - Score (1-5)\n"
        prompt += f"   - Justification\n"
        if i < len(dimensions_map):
            prompt += "\n"

    return prompt


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Extracting Optimized Prompts from DSPy COPRO")
    logger.info("=" * 60)
    logger.info("")

    # Step 1: Check if optimization results exist
    logger.info("Step 1: Checking for optimization results")
    module_dir = RESULTS_DIR / "optimized_module"
    summary_path = RESULTS_DIR / "optimization_summary.json"

    if not module_dir.exists():
        logger.error(f"❌ Optimized module directory not found: {module_dir}")
        logger.error("   Please run optimize_prompt.py first")
        return

    if not summary_path.exists():
        logger.error(f"❌ Optimization summary not found: {summary_path}")
        logger.error("   Please run optimize_prompt.py first")
        return

    logger.info(f"✓ Found optimized module in {module_dir}")
    logger.info(f"✓ Found optimization summary in {summary_path}")
    logger.info("")

    # Step 2: Configure DSPy
    logger.info("Step 2: Configuring DSPy")
    lm = dspy.LM(
        model=f"ollama/{OLLAMA_MODEL}",
        api_base=OLLAMA_BASE_URL,
        max_tokens=OLLAMA_MAX_TOKENS,
        temperature=OLLAMA_TEMPERATURE
    )
    dspy.settings.configure(lm=lm)
    logger.info("✓ DSPy configured")
    logger.info("")

    # Step 3: Load optimized module
    logger.info("Step 3: Loading optimized module")
    module_path = module_dir / "program.json"
    if not module_path.exists():
        logger.error(f"❌ Module file not found: {module_path}")
        return

    try:
        module = ConversationScoringModule()
        module.load(str(module_path))
        logger.info("✓ Optimized module loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load optimized module: {e}")
        return
    logger.info("")

    # Step 4: Extract prompts
    logger.info("Step 4: Extracting prompts from signature")
    try:
        # Debug: inspect the predictor structure
        logger.info(f"  Predictor type: {type(module.scorer)}")
        logger.info(f"  Predictor attributes: {dir(module.scorer)}")

        prompts = extract_signature_prompts(module)
        logger.info(f"✓ Extracted main instructions ({len(str(prompts['main_instructions']))} chars)")
        logger.info(f"✓ Extracted {len(prompts['field_prompts'])} field-level prompts")
    except Exception as e:
        logger.error(f"❌ Failed to extract prompts: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    logger.info("")

    # Step 5: Load performance summary
    logger.info("Step 5: Loading performance summary")
    try:
        with open(summary_path, 'r') as f:
            summary = json.load(f)
        logger.info("✓ Performance summary loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load summary: {e}")
        return
    logger.info("")

    # Step 6: Format as markdown
    logger.info("Step 6: Formatting as markdown")
    try:
        markdown_content = format_as_markdown(prompts, summary)
        logger.info(f"✓ Generated {len(markdown_content)} characters of markdown")
    except Exception as e:
        logger.error(f"❌ Failed to format markdown: {e}")
        return
    logger.info("")

    # Step 7: Save to file
    logger.info("Step 7: Saving to OPTIMIZED-SYSTEM-PROMPT.md")
    output_path = RESULTS_DIR.parent / "OPTIMIZED-SYSTEM-PROMPT.md"
    try:
        with open(output_path, 'w') as f:
            f.write(markdown_content)
        logger.info(f"✓ Saved to {output_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        return
    logger.info("")

    # Step 8: Create and save clean API-ready prompt
    logger.info("Step 8: Creating clean API-ready prompt (OPTIMIZED-PROMPT.txt)")
    try:
        clean_prompt = create_clean_prompt(prompts)
        clean_output_path = RESULTS_DIR.parent / "OPTIMIZED-PROMPT.txt"
        with open(clean_output_path, 'w') as f:
            f.write(clean_prompt)
        logger.info(f"✓ Saved clean prompt to {clean_output_path}")
        logger.info(f"✓ Clean prompt size: {len(clean_prompt)} characters")
    except Exception as e:
        logger.error(f"❌ Failed to create clean prompt: {e}")
        return
    logger.info("")

    # Summary
    logger.info("=" * 60)
    logger.info("✓ EXTRACTION COMPLETE!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Output files:")
    logger.info("  - OPTIMIZED-SYSTEM-PROMPT.md (full documentation)")
    logger.info("  - OPTIMIZED-PROMPT.txt (clean API-ready prompt)")
    logger.info("")
    logger.info("OPTIMIZED-SYSTEM-PROMPT.md contains:")
    logger.info("  - Performance improvement metrics")
    logger.info("  - Main system instruction")
    logger.info("  - Field-level prompts for all 10 output fields")
    logger.info("  - Usage examples and implementation details")
    logger.info("")
    logger.info("OPTIMIZED-PROMPT.txt contains:")
    logger.info("  - Clean prompt ready for any LLM API (OpenAI, Anthropic, etc.)")
    logger.info("  - No DSPy-specific code or documentation")
    logger.info("  - Copy-paste ready system prompt")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Use OPTIMIZED-PROMPT.txt in your API calls")
    logger.info("  2. Compare with BASELINE-PROMPT.txt")
    logger.info("  3. Review documentation in OPTIMIZED-SYSTEM-PROMPT.md")
    logger.info("")


if __name__ == "__main__":
    main()
