# llm_adapter.py
# Adapter for LLM calls — now using Groq API with LLaMA model

import os
import json
from dotenv import load_dotenv

load_dotenv()

USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def llm_call_system(prompt: str, max_tokens=512):
    """
    Generic LLM adapter. Uses Groq with LLaMA model if enabled.
    Returns text (preferably JSON).
    """
    if not USE_GROQ or not GROQ_API_KEY:
        return llm_fallback(prompt)

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        # Use a Groq-hosted LLaMA model
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # you can switch to "llama-3.1-70b" if needed
            messages=[
                {"role": "system", "content": "You are an agricultural planning assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )

        result = response.choices[0].message.content
        return result

    except Exception as e:
        print("⚠️ Groq API error:", e)
        return llm_fallback(prompt)

def llm_fallback(prompt: str):
    """
    Offline fallback if Groq API is unavailable or disabled.
    Provides deterministic structured reasoning.
    """
    plan = {"Compost": 45, "Biochar": 30, "Biogas": 20, "Feed_or_Storage": 5}
    reasoning = (
        "Fallback reasoning: Clay soil favors compost due to high nutrient retention; "
        "biochar limited to maintain soil aeration; biogas set for energy recovery."
    )
    return json.dumps({
        "plan": plan,
        "reasoning": reasoning,
        "confidence": 0.7
    })
