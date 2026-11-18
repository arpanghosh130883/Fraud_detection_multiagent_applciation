"""Base agent class — wraps OpenAI chat completions and handles JSON parsing."""

import json
import re
from typing import Any

from openai import OpenAI


class BaseAgent:
    def __init__(
        self,
        client: OpenAI,
        name: str,
        system_prompt: str,
        model: str = "gpt-4o-mini",
    ):
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.model = model

    def call_llm(self, user_message: str) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return self._parse_response(response.choices[0].message.content or "")

    def _parse_response(self, text: str) -> dict[str, Any]:
        # Strip markdown code fences if present
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try bare JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        return {"raw_response": text, "parse_error": True}
