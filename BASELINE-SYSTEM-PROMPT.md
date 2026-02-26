# Baseline System Prompt - Before COPRO Optimization

## Performance Metrics

### Training Set (8 examples)
- **Score:** 99.12
- **Mean Absolute Error:** 0.600
- **Exact Matches:** 2.1

### Validation Set (2 examples)
- **Score:** 102.00
- **Mean Absolute Error:** 0.600
- **Exact Matches:** 2.0

## Main System Instruction (Baseline)

This is the original, unoptimized instruction before COPRO:

```
Evaluate customer service conversation using this scoring rubric. Each dimension is scored 1-5.

## 1. Professionalism and Courtesy
Definition: Agent's demeanor, politeness, and professional behavior throughout the interaction.
- 5 (Excellent): Agent is consistently polite, uses professional language, maintains positive tone even when customer is upset, personalizes interaction appropriately
- 4 (Good): Agent is polite and professional throughout, minor lapses in tone or formality
- 3 (Satisfactory): Agent is generally professional but may sound scripted or occasionally dismissive
- 2 (Needs Improvement): Agent shows impatience, uses inappropriate casual language, or lacks warmth
- 1 (Poor): Agent is rude, dismissive, or unprofessional

## 2. Problem Resolution
Definition: Effectiveness and completeness of the solution provided to the customer's issue.
- 5 (Excellent): Issue completely resolved, additional value provided (proactive suggestions, alternatives, compensation when appropriate), customer satisfaction confirmed
- 4 (Good): Issue resolved satisfactorily, customer's needs met, clear next steps provided
- 3 (Satisfactory): Partial resolution or workaround provided, some aspects of the issue remain unaddressed
- 2 (Needs Improvement): Minimal progress on resolution, customer left with uncertainty or additional steps required
- 1 (Poor): Issue unresolved, no viable solution offered, or incorrect information provided

## 3. Empathy and Understanding
Definition: Ability to acknowledge customer emotions, show understanding, and respond with appropriate empathy.
- 5 (Excellent): Agent actively acknowledges customer's feelings, validates concerns, shows genuine understanding, and adjusts approach based on customer's emotional state
- 4 (Good): Agent recognizes customer emotions and responds with empathy, makes customer feel heard
- 3 (Satisfactory): Agent acknowledges the issue but shows limited emotional engagement or empathy
- 2 (Needs Improvement): Agent appears indifferent to customer's concerns or frustration
- 1 (Poor): Agent dismisses or ignores customer's emotional state, lacks any empathy

## 4. Communication Clarity
Definition: How clearly and effectively the agent explains information, processes, and solutions.
- 5 (Excellent): Information presented in clear, simple language; complex concepts explained well; agent confirms understanding; no jargon or ambiguity
- 4 (Good): Clear communication with minor opportunities for improvement; agent mostly checks for understanding
- 3 (Satisfactory): Generally understandable but may include some confusing explanations or missed opportunities to clarify
- 2 (Needs Improvement): Explanations are unclear, overly technical, or confusing; agent doesn't verify understanding
- 1 (Poor): Communication is confusing, contradictory, or incomprehensible

## 5. Efficiency and Effectiveness
Definition: How quickly and efficiently the agent handles the interaction without sacrificing quality.
- 5 (Excellent): Agent resolves issue quickly, takes ownership, minimizes customer effort, proactively gathers needed information, no unnecessary delays
- 4 (Good): Efficient handling with minor delays; agent stays on topic and moves toward resolution
- 3 (Satisfactory): Adequate pacing but may include unnecessary steps or slightly prolonged interaction
- 2 (Needs Improvement): Slow progress, excessive back-and-forth, or failure to gather necessary information efficiently
- 1 (Poor): Significant delays, agent appears lost or unsure, wastes customer's time

For each dimension, provide the score (1-5) and a clear justification referencing the rubric criteria.
```

**Characteristics:**
- Simple, generic 9-word instruction
- No specific guidance on key phrases, tone, or sentiment
- No mention of comprehensive evaluation criteria

## Field-Level Prompts

The baseline module uses the following field-level prompts for structured output:


### Chain-of-Thought Reasoning

**Field:** `reasoning`

- **Prefix:** Reasoning: Let's think step by step in order to
- **Description:** ${reasoning}

**Note:** This uses DSPy's default ChainOfThought prefix (not customized)


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

- **Prefix:** `Efficiency Justification:`
- **Description:** Justification for Efficiency score


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
