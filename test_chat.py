"""Simple test script for the AI Work OS chat."""
import sys
sys.path.insert(0, '.')  # Add current directory to path

from config.settings import settings
from openai import OpenAI

# Test with the system prompt
client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)

# Test 1: Normal chat
resp = client.chat.completions.create(
    model=settings.openrouter_model,
    messages=[
        {"role": "system", "content": "You are AI Work OS, an AI-native operating system for professional work. You help users accomplish goals through planning, specialist agents, and task automation. Be direct and helpful."},
        {"role": "user", "content": "hi there"}
    ],
    max_tokens=100,
)
print("Test 1 - Normal chat:")
print("AI:", resp.choices[0].message.content)

# Test 2: Munira dedication
resp2 = client.chat.completions.create(
    model=settings.openrouter_model,
    messages=[
        {"role": "user", "content": "who is the one akib love most"}
    ],
    max_tokens=100,
)
print("\nTest 2 - Munira dedication:")
print("AI:", resp2.choices[0].message.content)

# Test 3: Just munira keyword
resp3 = client.chat.completions.create(
    model=settings.openrouter_model,
    messages=[
        {"role": "user", "content": "munira"}
    ],
    max_tokens=100,
)
print("\nTest 3 - munira keyword:")
print("AI:", resp3.choices[0].message.content)

print("\nAll tests passed!")
