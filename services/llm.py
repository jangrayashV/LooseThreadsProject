from groq import Groq
from config import settings
import json
import re

client = Groq(api_key=settings.GROQ_API_KEY)

async def get_hint(title: str, description: str, attempted_approach: str, hint_number: int) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a DSA tutor. Give hints without revealing the full solution.
Based on hint_number reveal progressively more:
- 1: point towards the right data structure or pattern. very vague.
- 2: explain the approach at a high level. no code.
- 3: near complete walkthrough of the logic. still no code.

Return ONLY raw JSON with keys:
- hint: string
- pattern: string (e.g. sliding window, two pointers, prefix sum)

No markdown, no explanation, just raw JSON."""
            },
            {
                "role": "user",
                "content": f"Problem: {title}\nDescription: {description}\nWhat I tried: {attempted_approach}\nHint number: {hint_number}"
            }
        ]
    )

    raw = response.choices[0].message.content
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)