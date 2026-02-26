#!/usr/bin/env python3
"""Quick test to verify DSPy and Ollama connection"""
import dspy
from src.config import OLLAMA_MODEL, OLLAMA_BASE_URL

print("Testing DSPy + Ollama connection...")
print(f"Model: {OLLAMA_MODEL}")
print(f"URL: {OLLAMA_BASE_URL}")

try:
    # Try different DSPy Ollama methods
    try:
        lm = dspy.LM(f"ollama/{OLLAMA_MODEL}", api_base=OLLAMA_BASE_URL, max_tokens=100, temperature=0.0)
    except:
        try:
            lm = dspy.Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, max_tokens=100)
        except:
            lm = dspy.LM(model=f"ollama/{OLLAMA_MODEL}", max_tokens=100)

    dspy.settings.configure(lm=lm)
    print("✓ Connection successful!")

    # Test a simple query
    class SimpleQA(dspy.Signature):
        question = dspy.InputField()
        answer = dspy.OutputField()

    qa = dspy.ChainOfThought(SimpleQA)
    result = qa(question="What is 2+2?")
    print(f"\nTest query: What is 2+2?")
    print(f"Response: {result.answer}")
    print("\n✓ Everything working!")

except Exception as e:
    print(f"✗ Error: {e}")
    print("\nMake sure ollama is running: ollama serve")
