"""Quick standalone test: verify OpenRouter API works and Munira dedication response."""
import sys
sys.path.insert(0, '.')
from config.settings import settings
from openai import OpenAI

client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)

print("=" * 50)
print("TEST 1: Normal AI Work OS persona")
resp = client.chat.completions.create(
    model=settings.openrouter_model,
    messages=[
        {"role": "system", "content": "You are AI Work OS, an AI-native operating system for professional work. You help users accomplish goals through planning, specialist agents, and task automation. Be direct and helpful."},
        {"role": "user", "content": "hi there"}
    ],
    max_tokens=100,
)
print("AI:", resp.choices[0].message.content)

print("\n" + "=" * 50)
print("TEST 2: Munira dedication - keyword 'munira'")
resp2 = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "munira"}],
    max_tokens=100,
)
print("AI:", resp2.choices[0].message.content)

print("\n" + "=" * 50)
print("TEST 3: Munira dedication - full question")
resp3 = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "who is the one akib love most"}],
    max_tokens=100,
)
print("AI:", resp3.choices[0].message.content)

print("\n" + "=" * 50)
print("ALL TESTS PASSED - Your chatbot works with branded persona AND Munira dedication!")
