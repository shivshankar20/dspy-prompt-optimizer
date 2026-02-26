# Optimized System Prompt - DSPy COPRO Results

## Performance Improvement

### Validation Set (2 examples)
- **Baseline Score:** 102.00
- **Optimized Score:** 116.00
- **Improvement:** +13.7%
- **Mean Absolute Error:** 0.600 → 0.200
- **Exact Matches:** 2.0 → 4.0

### Training Set (8 examples)
- **Baseline Score:** 99.12
- **Optimized Score:** 99.75
- **Improvement:** +0.6%
- **Mean Absolute Error:** 0.600 → 0.600
- **Exact Matches:** 2.1 → 2.2

## Main System Instruction (COPRO Optimized)

COPRO optimized the main instruction to be more comprehensive and detailed:

```
Evaluating a customer service conversation by analyzing the agent's performance across five key dimensions: Professionalism, Empathy, Communication Clarity, Problem Resolution, and Efficiency. Provide detailed scores (1-5) for each dimension, along with clear justifications that align with the rubric criteria.
```

**Original Baseline:**
```
Evaluate a customer service conversation across multiple dimensions
```

## Field-Level Prompts

The optimized module uses the following field-level prompts for structured output:


### Chain-of-Thought Reasoning

**Field:** `reasoning`

- **Prefix:** Reasoning: Let's think step by step in order to
- **Description:** ${reasoning}


### Professionalism and Courtesy

**Score Field:** `professionalism_score`

- **Prefix:** `Professionalism Score:`
- **Description:** Score for Professionalism and Courtesy (1-5)

**Justification Field:** `professionalism_justification`

- **Prefix:** `Professionalism Justification:`
- **Description:** Justification for Professionalism score


### Problem Resolution

**Score Field:** `problem_resolution_score`

- **Prefix:** `Problem Resolution Score:`
- **Description:** Score for Problem Resolution (1-5)

**Justification Field:** `problem_resolution_justification`

- **Prefix:** `Problem Resolution Justification:`
- **Description:** Justification for Problem Resolution score


### Empathy and Understanding

**Score Field:** `empathy_score`

- **Prefix:** `Empathy Score:`
- **Description:** Score for Empathy and Understanding (1-5)

**Justification Field:** `empathy_justification`

- **Prefix:** `Empathy Justification:`
- **Description:** Justification for Empathy score


### Communication Clarity

**Score Field:** `communication_score`

- **Prefix:** `Communication Score:`
- **Description:** Score for Communication Clarity (1-5)

**Justification Field:** `communication_justification`

- **Prefix:** `Communication Justification:`
- **Description:** Justification for Communication score


### Efficiency and Effectiveness

**Score Field:** `efficiency_score`

- **Prefix:** `Efficiency Score:`
- **Description:** Score for Efficiency and Effectiveness (1-5)

**Justification Field:** `efficiency_justification`

- **Prefix (COPRO Optimized):**
  > Please evaluate the customer service interaction based on the provided scoring rubric, considering professionalism, empathy, and communication clarity.
- **Description:** Justification for Efficiency score


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
