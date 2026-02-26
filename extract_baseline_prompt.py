#!/usr/bin/env python3
"""
Extract baseline prompts from DSPy signature before COPRO optimization

This script:
1. Creates a fresh ConversationScoringModule (unoptimized baseline)
2. Extracts prompts from the signature (main instructions + field-level prompts)
3. Formats them as markdown and saves to BASELINE-SYSTEM-PROMPT.md
4. Creates clean API-ready prompt and saves to BASELINE-PROMPT.txt
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
    Extract prompts from the baseline module's signature

    Args:
        module: The baseline (unoptimized) ConversationScoringModule

    Returns:
        Dict containing main instructions and field-level prompts
    """
    # Get the ChainOfThought predictor
    predictor = module.scorer

    # Access the baseline signature
    if hasattr(predictor, 'predict') and hasattr(predictor.predict, 'signature'):
        signature = predictor.predict.signature
    elif hasattr(predictor, 'signature'):
        signature = predictor.signature
    else:
        # Fallback to the base signature class
        from src.dspy_signatures import ConversationScoring
        signature = ConversationScoring

    # Extract main instructions (baseline - unoptimized)
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


def format_as_markdown(prompts: dict, baseline_metrics: dict) -> str:
    """
    Format extracted baseline prompts as markdown

    Args:
        prompts: Dict with main_instructions and field_prompts
        baseline_metrics: Baseline performance metrics

    Returns:
        Formatted markdown string
    """
    train_metrics = baseline_metrics['train']
    val_metrics = baseline_metrics['validation']

    md = f"""# Baseline System Prompt - Before COPRO Optimization

## Performance Metrics

### Training Set (8 examples)
- **Score:** {train_metrics['avg_metric_score']:.2f}
- **Mean Absolute Error:** {train_metrics['avg_mae']:.3f}
- **Exact Matches:** {train_metrics['avg_exact_matches']:.1f}

### Validation Set (2 examples)
- **Score:** {val_metrics['avg_metric_score']:.2f}
- **Mean Absolute Error:** {val_metrics['avg_mae']:.3f}
- **Exact Matches:** {val_metrics['avg_exact_matches']:.1f}

## Main System Instruction (Baseline)

This is the original, unoptimized instruction before COPRO:

```
{prompts['main_instructions']}
```

**Characteristics:**
- Simple, generic 9-word instruction
- No specific guidance on key phrases, tone, or sentiment
- No mention of comprehensive evaluation criteria

## Field-Level Prompts

The baseline module uses the following field-level prompts for structured output:

"""

    # Group fields by dimension
    dimensions_map = {
        'professionalism': 'Professionalism and Courtesy',
        'problem_resolution': 'Problem Resolution',
        'empathy': 'Empathy and Understanding',
        'communication': 'Communication Clarity',
        'efficiency': 'Efficiency and Effectiveness'
    }

    # Check for reasoning field (baseline doesn't have custom reasoning)
    if 'reasoning' in prompts['field_prompts']:
        md += f"\n### Chain-of-Thought Reasoning\n\n"
        field_data = prompts['field_prompts']['reasoning']
        md += f"**Field:** `reasoning`\n\n"
        if field_data['prefix']:
            md += f"- **Prefix:** {field_data['prefix']}\n"
        if field_data['description']:
            md += f"- **Description:** {field_data['description']}\n"
        md += "\n**Note:** This uses DSPy's default ChainOfThought prefix (not customized)\n\n"

    for field_prefix, dimension_name in dimensions_map.items():
        md += f"\n### {dimension_name}\n\n"

        # Score field
        score_field = f"{field_prefix}_score"
        if score_field in prompts['field_prompts']:
            field_data = prompts['field_prompts'][score_field]
            md += f"**Score Field:** `{score_field}`\n\n"
            if field_data['prefix']:
                md += f"- **Prefix:** `{field_data['prefix']}`\n"
            else:
                md += f"- **Prefix:** _(uses DSPy default)_\n"
            if field_data['description']:
                md += f"- **Description:** {field_data['description']}\n"
            md += "\n"

        # Justification field
        just_field = f"{field_prefix}_justification"
        if just_field in prompts['field_prompts']:
            field_data = prompts['field_prompts'][just_field]
            md += f"**Justification Field:** `{just_field}`\n\n"
            if field_data['prefix']:
                md += f"- **Prefix:** `{field_data['prefix']}`\n"
            else:
                md += f"- **Prefix:** _(uses DSPy default)_\n"
            if field_data['description']:
                md += f"- **Description:** {field_data['description']}\n"
            md += "\n"

    md += """
## Baseline Characteristics

**What makes this baseline:**
- Generic main instruction without specific evaluation criteria
- Simple field descriptions with no custom prefixes
- No explicit guidance on what aspects to evaluate
- No mention of key phrases, tone, sentiment analysis
- Basic ChainOfThought with default DSPy configuration

**Comparison Points:**
- Main instruction: 9 words (generic)
- Field prompts: Standard descriptions only
- No optimization applied

## What COPRO Changed

COPRO optimization resulted in the following improvements:

1. **Main Instruction:** Expanded to 50+ words with detailed guidance
   - Added: "identifying key phrases, tone, sentiment"
   - Added: "response efficacy across multiple dimensions"
   - Added: "considering both customer's perspective and representative's approach"

2. **Field Prefixes:** Some fields got optimized custom prefixes
   - Example: `efficiency_justification` got a comprehensive assessment prompt

3. **Performance:** Training score improved by +2.3% (96.5 → 98.75)

See `OPTIMIZED-SYSTEM-PROMPT.md` for the full optimized version.

## Usage

This baseline prompt represents the starting point before optimization:

```python
import dspy
from src.dspy_signatures import ConversationScoringModule

# Create baseline (unoptimized) module
module = ConversationScoringModule()

# Score a conversation (without optimization)
result = module(conversation=conversation_text)
print(result['scores'])
print(result['justifications'])
```

## Notes

- This is the unoptimized baseline before COPRO optimization
- Baseline performance: 96.5 train, 116.0 validation
- COPRO improved training score by +2.3%
- See `OPTIMIZED-SYSTEM-PROMPT.md` for the optimized version
- See `results/optimization_summary.json` for detailed comparison
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

    # Add output structure
    prompt += "For each conversation, provide scores (1-5) and justifications for the following dimensions:\n\n"

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
    logger.info("Extracting Baseline Prompts (Before COPRO)")
    logger.info("=" * 60)
    logger.info("")

    # Step 1: Check if baseline results exist
    logger.info("Step 1: Checking for baseline results")
    baseline_path = RESULTS_DIR / "baseline_results.json"

    if not baseline_path.exists():
        logger.error(f"❌ Baseline results not found: {baseline_path}")
        logger.error("   Please run optimize_prompt.py first")
        return

    logger.info(f"✓ Found baseline results in {baseline_path}")
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

    # Step 3: Create baseline (unoptimized) module
    logger.info("Step 3: Creating baseline (unoptimized) module")
    try:
        module = ConversationScoringModule()
        logger.info("✓ Baseline module created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create baseline module: {e}")
        return
    logger.info("")

    # Step 4: Extract prompts
    logger.info("Step 4: Extracting prompts from baseline signature")
    try:
        prompts = extract_signature_prompts(module)
        logger.info(f"✓ Extracted main instructions ({len(str(prompts['main_instructions']))} chars)")
        logger.info(f"✓ Extracted {len(prompts['field_prompts'])} field-level prompts")

        # Show what we extracted
        logger.info(f"\nBaseline main instruction:")
        logger.info(f"  '{prompts['main_instructions']}'")
    except Exception as e:
        logger.error(f"❌ Failed to extract prompts: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    logger.info("")

    # Step 5: Load baseline metrics
    logger.info("Step 5: Loading baseline metrics")
    try:
        with open(baseline_path, 'r') as f:
            baseline_metrics = json.load(f)
        logger.info("✓ Baseline metrics loaded")
        logger.info(f"  Training score: {baseline_metrics['train']['avg_metric_score']:.2f}")
        logger.info(f"  Validation score: {baseline_metrics['validation']['avg_metric_score']:.2f}")
    except Exception as e:
        logger.error(f"❌ Failed to load baseline metrics: {e}")
        return
    logger.info("")

    # Step 6: Format as markdown
    logger.info("Step 6: Formatting as markdown")
    try:
        markdown_content = format_as_markdown(prompts, baseline_metrics)
        logger.info(f"✓ Generated {len(markdown_content)} characters of markdown")
    except Exception as e:
        logger.error(f"❌ Failed to format markdown: {e}")
        return
    logger.info("")

    # Step 7: Save to file
    logger.info("Step 7: Saving to BASELINE-SYSTEM-PROMPT.md")
    output_path = RESULTS_DIR.parent / "BASELINE-SYSTEM-PROMPT.md"
    try:
        with open(output_path, 'w') as f:
            f.write(markdown_content)
        logger.info(f"✓ Saved to {output_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        return
    logger.info("")

    # Step 8: Create and save clean API-ready prompt
    logger.info("Step 8: Creating clean API-ready prompt (BASELINE-PROMPT.txt)")
    try:
        clean_prompt = create_clean_prompt(prompts)
        clean_output_path = RESULTS_DIR.parent / "BASELINE-PROMPT.txt"
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
    logger.info("  - BASELINE-SYSTEM-PROMPT.md (full documentation)")
    logger.info("  - BASELINE-PROMPT.txt (clean API-ready prompt)")
    logger.info("")
    logger.info("BASELINE-SYSTEM-PROMPT.md contains:")
    logger.info("  - Baseline performance metrics")
    logger.info("  - Original unoptimized main instruction")
    logger.info("  - Field-level prompts for all output fields")
    logger.info("  - Comparison notes with COPRO optimization")
    logger.info("")
    logger.info("BASELINE-PROMPT.txt contains:")
    logger.info("  - Clean prompt ready for any LLM API (OpenAI, Anthropic, etc.)")
    logger.info("  - No DSPy-specific code or documentation")
    logger.info("  - Copy-paste ready system prompt")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Use BASELINE-PROMPT.txt in your API calls")
    logger.info("  2. Compare with OPTIMIZED-PROMPT.txt")
    logger.info("  3. Review documentation in BASELINE-SYSTEM-PROMPT.md")
    logger.info("")


if __name__ == "__main__":
    main()
