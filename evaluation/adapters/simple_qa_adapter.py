"""Simple QA adapter for LOCOMO evaluation - minimal baseline."""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Add nanomemo to path (go up two levels: adapters -> evaluation -> nanomemo)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python"))

from nanomemo import Memory
from openai import OpenAI


class SimpleQAAdapter:
    """Simple QA agent that stores conversations and answers questions."""

    def __init__(self, memory_path: str, model: str = "gpt-4o-mini"):
        """Initialize simple QA adapter."""
        self.memory = Memory(memory_path)
        self.model = model

        # Read API key and base URL from environment
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

        # Ensure directory structure
        (Path(memory_path) / "conversations").mkdir(parents=True, exist_ok=True)

    def process_turn(self, turn: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Store conversation turn directly to memory.

        Simple approach: append each turn to a session conversation file.
        """
        speaker = turn.get("speaker", "unknown")
        content = turn.get("content", "")

        # Store in session-specific file
        session_file = f"conversations/{session_id}.md"

        try:
            # Try to read existing conversation (returns content without frontmatter)
            existing = self.memory.read(session_file)
            # Strip frontmatter if present (read() should already do this, but be safe)
            if existing.startswith("---"):
                parts = existing.split("---\n", 2)
                if len(parts) >= 3:
                    existing = parts[2]

            # Append new turn
            new_content = existing.rstrip() + f"\n\n**{speaker}**: {content}"
            self.memory.update(session_file, new_content)
        except FileNotFoundError:
            # Create new conversation file
            new_content = f"# Conversation: {session_id}\n\n**{speaker}**: {content}"
            self.memory.write(
                path=session_file,
                content=new_content,
                summary=f"Conversation between participants in {session_id}",
                tags=["conversation", session_id],
            )

        return {"status": "ok"}

    def answer_question(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        Answer question using conversation memory.
        """
        start_time = time.time()

        # Read the conversation for this session
        session_file = f"conversations/{session_id}.md"

        try:
            conversation = self.memory.read(session_file)
        except FileNotFoundError:
            conversation = "No conversation found."

        # Generate answer using conversation context
        prompt = f"""Answer the following question using only the information from the conversation provided.

Question: {question}

Conversation:
{conversation}

If the conversation doesn't contain enough information to answer the question, say "I don't have enough information to answer that."

Provide a concise, direct answer."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )

            answer = response.choices[0].message.content or "No answer generated."
            tokens_used = response.usage.total_tokens if response.usage else 0

        except Exception as e:
            print(f"Error generating answer: {e}")
            answer = f"Error: {str(e)}"
            tokens_used = 0

        latency = time.time() - start_time

        return {
            "answer": answer,
            "latency": latency,
            "tokens_used": tokens_used,
            "memories_retrieved": 1,
        }
