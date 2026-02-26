"""Configuration settings for DSPy COPRO optimization"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUTS_DIR = PROJECT_ROOT / "inputs"
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULTS_DIR = PROJECT_ROOT / "results"

# Ollama configuration
OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MAX_TOKENS = 2000
OLLAMA_TEMPERATURE = 0.0

# Scoring dimensions
DIMENSIONS = [
    "Professionalism and Courtesy",
    "Problem Resolution",
    "Empathy and Understanding",
    "Communication Clarity",
    "Efficiency and Effectiveness"
]

# COPRO optimization parameters
COPRO_BREADTH = 10  # Number of prompt variants per iteration
COPRO_DEPTH = 3     # Number of optimization rounds
COPRO_INIT_TEMP = 1.0
COPRO_NUM_THREADS = 1  # Single-threaded to limit resource usage

# Train/validation split
# Train: conversations 1,2,3,5,6,7,9,10 (8 examples)
# Val: conversations 4,8 (2 examples)
TRAIN_IDS = [1, 2, 3, 5, 6, 7, 9, 10]
VAL_IDS = [4, 8]

# Create results directory if it doesn't exist
RESULTS_DIR.mkdir(exist_ok=True)
