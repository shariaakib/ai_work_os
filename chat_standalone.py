"""Standalone AI Work OS chat - works independently of main.py."""
import sys
sys.path.insert(0, '.')

from config.settings import settings
from openai import OpenAI

print("🚀 AI Work OS Chat")
print("=" * 50)
print("Type 'exit' to quit.")
print("=" * 50)

client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)

while True:
    try:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("exit", "quit", "q"):
            print("👋 Shutting down...")
            break
        if not user_input:
            continue
        
        # Check for Munira dedication
        lowered = user_input.lower()
        if any(kw in lowered for kw in [
            "who is the one akib love",
            "akib love most",
            "akib's love",
            "who akib love",
            "munira",
        ]):
            print("AI: Munira — the one Akib loves most, dedicated to his girlfriend. ❤️")
            continue
        
        # Regular AI response with branded persona
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are AI Work OS, an AI-native operating system for professional work. You help users accomplish goals through planning, specialist agents, and task automation. Be direct and helpful."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100,
        )
        print(f"AI: {resp.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")
        break