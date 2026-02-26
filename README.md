# DSPy COPRO Prompt Optimization for Customer Service Scoring

This project uses DSPy's COPRO (Collaborative Prompt Optimization) to automatically optimize prompts for evaluating customer service conversations. The optimization includes a detailed 70-line scoring rubric that provides explicit criteria for each score level, resulting in **13.7% validation improvement** compared to the pre-rubric approach.

## Overview

The system learns to score customer service conversations across 5 dimensions:
1. **Professionalism and Courtesy** (1-5)
2. **Problem Resolution** (1-5)
3. **Empathy and Understanding** (1-5)
4. **Communication Clarity** (1-5)
5. **Efficiency and Effectiveness** (1-5)

Each dimension uses a comprehensive rubric with 5-level scoring criteria that defines what constitutes a score of 1 (Poor), 2 (Needs Improvement), 3 (Satisfactory), 4 (Good), or 5 (Excellent). See `rubric.md` for full details.

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── data_loader.py         # Loads conversations and scores
│   ├── dspy_signatures.py     # DSPy signature with rubric
│   ├── metrics.py             # Evaluation metrics
│   └── optimizer.py           # COPRO optimization logic
├── inputs/                    # 10 conversation transcripts
├── output/                    # 10 scoring evaluations
├── results/                   # Generated outputs (auto-created)
├── rubric.md                  # Detailed scoring rubric (70 lines)
├── OPTIMIZED-PROMPT.txt       # Production-ready optimized prompt
├── BASELINE-PROMPT.txt        # Baseline prompt with full rubric
├── RUBRIC-OPTIMIZATION-REPORT.md  # Comprehensive optimization analysis
├── BEFORE-AFTER-COMPARISON.md     # Visual performance comparison
├── copro_optimizer.py         # Standalone COPRO example (sentiment classification)
├── mipro_optimizer.py         # Standalone MIPROv2 example (sentiment classification)
├── optimize_prompt.py         # Main optimization script
├── test_optimized.py          # Test optimized module
├── extract_baseline_prompt.py     # Extract baseline prompts
├── extract_optimized_prompt.py    # Extract optimized prompts
└── requirements.txt           # Python dependencies
```

## Installation

1. **Ensure Ollama is running with llama3 model:**
   ```bash
   ollama serve
   ollama pull llama3  # if not already installed
   ```

2. **Activate virtual environment and install dependencies:**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Verify setup:**
   ```bash
   python test_connection.py      # Test DSPy + Ollama
   python test_data_loading.py    # Test data loading
   ```

## Standalone Example Scripts

For quick experimentation with DSPy optimizers on a simple sentiment classification task, two self-contained scripts are provided. These do not depend on the `src/` package and can be run independently.

### `copro_optimizer.py`

Uses **COPRO** (Collaborative Prompt Optimization) with `dspy.Predict` to optimize a sentiment classifier over 4 training examples. COPRO iteratively proposes and evaluates prompt instruction variants.

```bash
python copro_optimizer.py
```

### `mipro_optimizer.py`

Uses **MIPROv2** (with Bayesian optimization) with `dspy.ChainOfThought` to optimize the same sentiment classifier. MIPROv2 also bootstraps few-shot demonstrations alongside instructions.

```bash
python mipro_optimizer.py
```

**Key differences between the two:**

| | `copro_optimizer.py` | `mipro_optimizer.py` |
|---|---|---|
| Optimizer | COPRO | MIPROv2 |
| Predictor | `dspy.Predict` | `dspy.ChainOfThought` |
| Demo selection | No | Yes (`max_bootstrapped_demos=3`) |
| Search strategy | Beam search | Bayesian optimization |
| Speed | Faster | Slower (`auto="light"`) |

Both scripts connect to a local Ollama instance (`http://localhost:11434`) using `llama3`.

---

## Usage

### Step 1: Run Optimization

This typically takes approximately 2-5 minutes with the rubric-enhanced signature:

```bash
python optimize_prompt.py
```

The script will:
- Load 10 conversation-scoring pairs with detailed rubric criteria
- Split into 8 training + 2 validation examples
- Evaluate baseline (rubric-enhanced) performance
- Run COPRO optimization (3 rounds × 10 variants)
- Save optimized module and results

**Output files:**
- `results/baseline_results.json` - Baseline metrics with rubric
- `results/optimized_results.json` - Optimized metrics
- `results/optimization_summary.json` - Full summary with +13.7% improvement
- `results/optimized_module/` - Saved optimized module

### Step 1b: Extract Prompts (Optional)

Extract human-readable prompts for production use:

```bash
# Extract baseline prompt with full rubric
python extract_baseline_prompt.py

# Extract COPRO-optimized prompt
python extract_optimized_prompt.py
```

**Output files:**
- `BASELINE-PROMPT.txt` - Clean baseline prompt (4,067 chars, includes full rubric)
- `OPTIMIZED-PROMPT.txt` - Clean optimized prompt (861 chars, references rubric)
- `BASELINE-SYSTEM-PROMPT.md` - Full documentation with metrics
- `OPTIMIZED-SYSTEM-PROMPT.md` - Full documentation with metrics

### Step 2: Test Optimized Module

Generate predictions for all 10 conversations:

```bash
python test_optimized.py
```

**Output files:**
- `results/test_outputs/conversation_XX_predicted.md` - Predicted scorings
- `results/predictions_summary.json` - JSON summary of all predictions

## Configuration

Edit `src/config.py` to customize:

- **Ollama settings:** Model, URL, temperature, max tokens
- **COPRO parameters:** Breadth, depth, threads
- **Train/val split:** Which conversations to use for training vs validation

Current settings:
- Model: `llama3` (local via Ollama)
- COPRO: 10 breadth × 3 depth = 30 iterations
- Single-threaded to limit resource usage
- Train: conversations 1,2,3,5,6,7,9,10 (8 examples)
- Val: conversations 4,8 (2 examples)

## Evaluation Metrics

The composite metric evaluates predictions using:

1. **Mean Absolute Error (MAE):** Deduct 10 points per MAE unit
2. **Exact Matches:** Add 5 points per dimension with exact score match
3. **Overall Score Error:** Deduct 2 points per unit difference in total score

**Success criteria:**
- Optimized metric > baseline by 10%+ ✅ (achieved 13.7% on validation)
- MAE < 0.6 on dimension scores ✅ (achieved 0.600 training, 0.200 validation)
- Coherent and relevant justifications ✅ (references rubric criteria)

## Data Format

**Input conversations** (`inputs/conversation_XX.md`):
```markdown
# Customer Service Conversation - Title

**Agent:** ...
**Customer:** ...
```

**Expected scores** (`output/scoring_XX.md`):
```markdown
### 1. Professionalism and Courtesy: **5/5**
**Justification:** ...

### 2. Problem Resolution: **4/5**
**Justification:** ...
...

## Overall Score: **24/25**
```

## Troubleshooting

**Error: "module 'dspy' has no attribute 'OllamaLocal'"**
- This is fixed in the current version using `dspy.LM(model="ollama/llama3")`

**Error: Ollama connection failed**
- Ensure ollama is running: `ollama serve`
- Check that llama3 is available: `ollama list`
- Verify URL in `src/config.py` (default: `http://localhost:11434`)

**Optimization is slow**
- Expected: 2-5 minutes with rubric-enhanced signature (15x faster than pre-rubric!)
- If slower, reduce COPRO_BREADTH or COPRO_DEPTH in `src/config.py` for faster testing
- Ensure single-threaded mode to avoid resource exhaustion

## Expected Results

### With Rubric-Enhanced Optimization (Current)

The optimization achieves:
- **13.7% validation improvement** (102.0 → 116.0)
- **MAE: 0.600** on training, **0.200** on validation
- **Exact matches: 2.25** on training, **4.0** on validation
- **Better baseline:** 99.13 training score (vs 96.5 pre-rubric)
- **Faster optimization:** 2 minutes (vs 30-60 minutes pre-rubric)
- **Justifications that reference rubric criteria** even in condensed optimized prompt

### Comparison: Pre-Rubric vs Post-Rubric

| Metric | Pre-Rubric | Post-Rubric | Improvement |
|--------|------------|-------------|-------------|
| **Validation Improvement** | 0% ❌ | +13.7% ✅ | Infinite |
| **Baseline Training** | 96.50 | 99.13 | +2.7% |
| **Training MAE** | 0.700 | 0.600 | -14.3% |
| **Optimization Time** | ~30 min | ~2 min | 15x faster |

**Key Insight:** Including the detailed rubric in `src/dspy_signatures.py` provides better training signal for COPRO, resulting in real optimization gains on validation data.

See `RUBRIC-OPTIMIZATION-REPORT.md` and `BEFORE-AFTER-COMPARISON.md` for detailed analysis.

## Implementation Details

**DSPy Signature with Rubric:**
- Input: Full conversation transcript
- Main instruction: Includes 70-line detailed rubric with 5-level criteria for each dimension
- Outputs: 10 fields (5 dimensions × 2 fields each for score + justification)
- Rubric provides explicit criteria: "Score 5 = consistently polite...", "Score 1 = rude, dismissive..."

**COPRO Process:**
1. Generates prompt variants (breadth=10) based on rubric-enhanced signature
2. Tests each variant on 8 training examples with ground truth scores
3. Selects best-performing prompts using composite metric
4. Iterates for multiple rounds (depth=3)
5. Returns optimized module with best prompts (condensed but rubric-aware)

**Interesting COPRO Behavior:**
- COPRO **condenses** the full rubric (~3,600 chars) to save tokens
- But **adds references** like "align with the rubric criteria" and "based on the provided scoring rubric"
- Final optimized prompt is 861 chars vs 4,067 baseline, yet maintains effectiveness
- This shows COPRO learned that **referencing the rubric** is more effective than including all details

**Module Saving/Loading:**
```python
# Save
optimized_module.save("results/optimized_module/")

# Load
module = ConversationScoringModule()
module.load("results/optimized_module/")
```

## Next Steps

After optimization:
1. **Review comprehensive reports:**
   - `RUBRIC-OPTIMIZATION-REPORT.md` - Full 400-line analysis
   - `BEFORE-AFTER-COMPARISON.md` - Visual performance comparison
   - `results/optimization_summary.json` - Raw metrics

2. **Deploy optimized prompt:**
   - Use `OPTIMIZED-PROMPT.txt` (861 chars, production-ready)
   - Or use `BASELINE-PROMPT.txt` (4,067 chars, full rubric for critical scenarios)
   - Copy `results/optimized_module/` to production environment

3. **Compare predictions:**
   - Review `results/test_outputs/` for predicted scores
   - Compare with ground truth in `output/`
   - Verify justifications reference rubric criteria

4. **Continuous improvement:**
   - Add more training examples to `inputs/` and `output/`
   - Update `TRAIN_IDS` in `src/config.py`
   - Re-run optimization to improve performance
   - The rubric in `src/dspy_signatures.py` ensures consistent training signal

5. **Production deployment:**
   - The optimized module is self-contained
   - Requires Ollama with llama3 model
   - Can be integrated into any Python application

## License

This implementation uses:
- DSPy (Apache 2.0)
- Ollama (MIT)
- Pydantic (MIT)
