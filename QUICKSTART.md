# Quick Start Guide

## Prerequisites

✓ Ollama running with llama3 model
✓ Python virtual environment activated
✓ Dependencies installed

## Standalone Examples (Optional)

Before running the full pipeline, you can try the self-contained optimizer examples that work on a simple sentiment classification task. These require no additional setup beyond Ollama being running.

**COPRO** — optimizes prompt instructions using beam search:
```bash
python copro_optimizer.py
```

**MIPROv2** — optimizes instructions + few-shot demos using Bayesian search:
```bash
python mipro_optimizer.py
```

Each script runs end-to-end (configure → train → test → inspect) in a few minutes and prints the optimized prompt at the end.

---

## Step 1: Verify Setup (1 minute)

```bash
# Test connection
python test_connection.py

# Test data loading
python test_data_loading.py
```

Expected output:
- ✓ Connection successful!
- ✓ Data loading successful!

## Step 2: Run Optimization (2-5 minutes)

```bash
python optimize_prompt.py
```

**What happens:**
1. Loads 8 training + 2 validation examples with detailed rubric criteria
2. Tests baseline (rubric-enhanced) module
3. Runs COPRO optimization (3 rounds × 10 variants = 30 iterations)
4. Saves optimized module to `results/optimized_module/`
5. Generates performance comparison showing +13.7% validation improvement

**Monitor progress:**
- Watch for "Testing on training set..." and "Testing on validation set..."
- COPRO will log progress for each iteration (much faster with rubric!)
- Final summary shows baseline vs optimized metrics
- Typical completion time: 2-5 minutes (vs 30-60 minutes pre-rubric)

## Step 3: Extract Prompts (1 minute)

```bash
# Extract baseline prompt with full rubric
python extract_baseline_prompt.py

# Extract COPRO-optimized prompt
python extract_optimized_prompt.py
```

**Output:**
- `BASELINE-PROMPT.txt` - Clean baseline (4,067 chars, full rubric)
- `OPTIMIZED-PROMPT.txt` - Clean optimized (861 chars, references rubric)
- `BASELINE-SYSTEM-PROMPT.md` - Full documentation
- `OPTIMIZED-SYSTEM-PROMPT.md` - Full documentation

## Step 4: Test Optimized Module (instant)

```bash
python test_optimized.py
```

**Output:**
- 10 predicted scoring files in `results/test_outputs/`
- JSON summary at `results/predictions_summary.json`
- Predictions reference rubric criteria in justifications

## Step 5: Review Results

### Check Comprehensive Reports

```bash
# Quick visual comparison
cat BEFORE-AFTER-COMPARISON.md

# Full 400-line analysis
cat RUBRIC-OPTIMIZATION-REPORT.md

# Raw metrics
cat results/optimization_summary.json
```

Look for:
- **validation_percent**: ✅ Achieved +13.7% improvement (vs 0% pre-rubric!)
- **avg_mae**: ✅ 0.600 training, 0.200 validation (excellent)
- **avg_exact_matches**: ✅ 2.25 training, 4.0 validation

### Compare Predictions

```bash
# View optimized prompt
cat OPTIMIZED-PROMPT.txt

# View a predicted scoring
cat results/test_outputs/conversation_01_predicted.md

# Compare with actual scoring
cat output/scoring_01.md
```

## Expected Results

### With Rubric-Enhanced Optimization (Current)

**Baseline metrics:**
- Training score: 99.13 (excellent!)
- Validation score: 102.00
- Training MAE: 0.600
- Validation MAE: 0.600

**Optimized metrics:**
- Training score: 99.75 (+0.6% improvement)
- Validation score: 116.00 (**+13.7% improvement** ✅)
- Training MAE: 0.600 (maintained)
- Validation MAE: 0.200 (67% improvement!)
- Exact matches: 4.0/5.0 on validation

### Pre-Rubric vs Post-Rubric

| Metric | Pre-Rubric | Post-Rubric | Winner |
|--------|------------|-------------|--------|
| Validation improvement | 0% ❌ | +13.7% ✅ | **Post-Rubric** |
| Baseline quality | 96.50 | 99.13 | **Post-Rubric** |
| Optimization time | ~30 min | ~2 min | **Post-Rubric** |

**Key takeaway:** The detailed rubric in `src/dspy_signatures.py` provides essential training signal for COPRO optimization.

## Troubleshooting

**Problem:** "module 'dspy' has no attribute 'OllamaLocal'"
- **Solution:** Already fixed - code uses `dspy.LM()` instead

**Problem:** Ollama connection error
- **Solution:** Run `ollama serve` in another terminal

**Problem:** Out of memory
- **Solution:** Close other applications, or reduce `COPRO_BREADTH` in `src/config.py`

**Problem:** Optimization too slow
- **Solution:** Should only take 2-5 minutes with rubric! If slower, reduce `COPRO_DEPTH` from 3 to 2 in `src/config.py`

## File Locations

| File | Description |
|------|-------------|
| `copro_optimizer.py` | Standalone COPRO example (sentiment classification) |
| `mipro_optimizer.py` | Standalone MIPROv2 example (sentiment classification) |
| `OPTIMIZED-PROMPT.txt` | Production-ready prompt (861 chars) |
| `BASELINE-PROMPT.txt` | Full rubric prompt (4,067 chars) |
| `RUBRIC-OPTIMIZATION-REPORT.md` | Comprehensive analysis |
| `BEFORE-AFTER-COMPARISON.md` | Visual comparison |
| `results/baseline_results.json` | Before optimization |
| `results/optimized_results.json` | After optimization |
| `results/optimization_summary.json` | Full comparison |
| `results/optimized_module/` | Saved optimized module |
| `results/test_outputs/*.md` | Predicted scorings |

## Next Steps

1. **Deploy the optimized prompt:**
   - Use `OPTIMIZED-PROMPT.txt` (861 chars, references rubric)
   - Or use `BASELINE-PROMPT.txt` (4,067 chars, full rubric for critical scenarios)
   - Copy-paste into any LLM API (OpenAI, Anthropic, etc.)

2. **Use optimized module on new conversations:**
   ```python
   from src.dspy_signatures import ConversationScoringModule
   module = ConversationScoringModule()
   module.load("results/optimized_module/")
   result = module(conversation="your conversation text")
   ```

3. **Understand the optimization:**
   - Read `RUBRIC-OPTIMIZATION-REPORT.md` for comprehensive analysis
   - Review `BEFORE-AFTER-COMPARISON.md` for visual performance comparison
   - See how COPRO condensed the rubric while maintaining effectiveness

4. **Add more training examples:**
   - Add new conversations to `inputs/`
   - Add corresponding scores to `output/`
   - Update `TRAIN_IDS` in `src/config.py`
   - Re-run optimization to improve further
   - The rubric in `src/dspy_signatures.py` ensures consistent training signal

5. **Export for production:**
   - The optimized module is self-contained
   - Copy `results/optimized_module/` to production
   - Load with `module.load("path/to/optimized_module")`
   - Requires Ollama with llama3 model

## Key Insights

### Why the Rubric Matters

**Before (No Rubric):**
- COPRO had no scoring criteria, only 8 examples
- Validation improvement: **0%** (baseline already maxed out)
- Optimization time: ~30 minutes

**After (With Rubric):**
- COPRO learned from explicit 5-level criteria for all dimensions
- Validation improvement: **+13.7%** (real optimization!)
- Optimization time: ~2 minutes (15x faster!)

**The rubric provides essential training signal for COPRO.** Even though COPRO condenses it in the final prompt (4,067 → 861 chars), the optimization process benefits from having explicit criteria.

### What COPRO Learned

COPRO intelligently:
- ❌ Removed the full 3,600-char rubric text (to save tokens)
- ✅ Added "align with the rubric criteria" and "based on the provided scoring rubric"
- ✅ Made the prompt cleaner and more concise
- ✅ Maintained effectiveness by referencing the rubric

This shows COPRO learned that **knowing a rubric exists** is more important than including all details.

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review `RUBRIC-OPTIMIZATION-REPORT.md` for comprehensive analysis
3. Review `BEFORE-AFTER-COMPARISON.md` for visual comparison
4. Check DSPy documentation: https://github.com/stanfordnlp/dspy
