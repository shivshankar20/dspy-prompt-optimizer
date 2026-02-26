#!/usr/bin/env python3
"""Test data loading functionality"""
import logging
from src.data_loader import load_example
from src.config import TRAIN_IDS, VAL_IDS

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("Testing data loading...")
print()

# Test loading one example
example = load_example(1)
print(f"Conversation ID: {example.conversation_id}")
print(f"Conversation length: {len(example.conversation)} characters")
print(f"Expected scores: {example.expected_scores}")
print(f"Overall score: {example.overall_score}")
print()

# Verify all dimensions present
print("Dimensions found:")
for dim, score in example.expected_scores.items():
    justification_preview = example.expected_justifications[dim][:50] + "..."
    print(f"  - {dim}: {score}/5")
    print(f"    Justification: {justification_preview}")
print()

print(f"✓ Data loading successful!")
print(f"\nTrain IDs: {TRAIN_IDS}")
print(f"Val IDs: {VAL_IDS}")
