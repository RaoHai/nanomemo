"""NanoMemo adapter for LOCOMO evaluation."""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI

# Add parent directory to path to import nanomemo (go up two levels)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python"))

from nanomemo import Memory


class NanoMemoAdapter:
    """Adapter for evaluating NanoMemo on LOCOMO dataset."""

    def __init__(self, memory_path: str, model: str = "gpt-4o-mini"):
        """
        Initialize NanoMemo adapter.

        Args:
            memory_path: Path to memory directory
            model: OpenAI model for entity extraction and answer generation
        """
        self.memory = Memory(memory_path)

        # Read API key and base URL from environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        # Initialize OpenAI client with environment variables
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

        self.model = model

        # Ensure memory structure exists
        for category in ["people", "events", "daily", "preferences"]:
            (Path(memory_path) / category).mkdir(parents=True, exist_ok=True)

    def process_turn(self, turn: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Process a conversation turn and store memories.

        Args:
            turn: Conversation turn with 'speaker' and 'content'
            session_id: Session identifier

        Returns:
            Metrics about the storage operation
        """
        print(f"[DEBUG] Processing turn from {turn.get('speaker', 'unknown')}: {turn.get('content', '')[:50]}...")
        start_time = time.time()
        tokens_used = 0

        # Extract entities and facts from the turn
        extraction_prompt = f"""Analyze this conversation turn and extract structured information to save to memory.

Turn: {turn['content']}
Speaker: {turn['speaker']}

Extract:
1. People mentioned (names, roles, relationships)
2. Events (what happened, when, where)
3. Preferences (likes, dislikes, habits)
4. Facts (any other important information)

Return JSON with:
{{
  "people": [{{"name": "...", "info": "..."}}],
  "events": [{{"description": "...", "date": "..."}}],
  "preferences": [{{"type": "...", "value": "..."}}],
  "facts": ["..."]
}}

If nothing significant to extract, return empty lists."""

        try:
            print(f"[DEBUG] Calling OpenAI API with model {self.model}...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                response_format={"type": "json_object"},
                temperature=0.0,
            )

            tokens_used = response.usage.total_tokens if response.usage else 0
            extracted = json.loads(response.choices[0].message.content or "{}")

            # Store extracted information
            self._store_people(extracted.get("people", []), session_id)
            self._store_events(extracted.get("events", []), session_id)
            self._store_preferences(extracted.get("preferences", []), session_id)

            # Always append to daily log
            self._append_daily_log(turn, session_id)

        except Exception as e:
            print(f"Error processing turn: {e}")

        latency = time.time() - start_time

        return {
            "latency": latency,
            "tokens_used": tokens_used,
        }

    def answer_question(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        Answer a question using memory.

        Args:
            question: Question to answer
            session_id: Session identifier

        Returns:
            Dict with 'answer', 'latency', 'tokens_used', 'memories_retrieved'
        """
        start_time = time.time()

        # Search for relevant memories
        search_results = self.memory.search_summaries(question, case_sensitive=False)

        # Also try content search if summary search returns few results
        if len(search_results) < 3:
            content_results = self.memory.search_content(question, case_sensitive=False)
            # Merge and deduplicate
            seen_paths = {r.path for r in search_results}
            for r in content_results:
                if r.path not in seen_paths:
                    search_results.append(r)
                    seen_paths.add(r.path)

        # Read top 5 relevant memories
        context_parts = []
        for result in search_results[:5]:
            try:
                content = self.memory.read(result.path)
                context_parts.append(f"## {result.path}\n{content}")
            except Exception as e:
                print(f"Error reading {result.path}: {e}")

        context = "\n\n".join(context_parts) if context_parts else "No relevant memories found."

        # Generate answer using context
        answer_prompt = f"""Answer the following question using only the information from the memory context provided.

Question: {question}

Memory Context:
{context}

If the memory context doesn't contain enough information to answer the question, say "I don't have enough information to answer that."

Provide a concise, direct answer."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": answer_prompt}],
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
            "memories_retrieved": len(search_results[:5]),
        }

    def _store_people(self, people: List[Dict], session_id: str) -> None:
        """Store or update person profiles."""
        for person in people:
            name = person.get("name", "").lower().replace(" ", "-")
            if not name:
                continue

            path = f"people/{name}.md"
            info = person.get("info", "")

            try:
                # Check if person file exists
                existing = self.memory.read(path)
                # Append new info
                self.memory.update(path, existing + f"\n\n## Update\n{info}")
            except FileNotFoundError:
                # Create new person file
                content = f"# {person.get('name', name)}\n\n{info}"
                self.memory.write(
                    path=path,
                    content=content,
                    summary=f"{person.get('name', name)} - {info[:50]}",
                    tags=["people"],
                )

    def _store_events(self, events: List[Dict], session_id: str) -> None:
        """Store events."""
        for event in events:
            description = event.get("description", "")
            if not description:
                continue

            # Use timestamp as filename
            filename = f"event-{int(time.time())}.md"
            path = f"events/{filename}"

            content = f"# Event\n\n{description}"
            if date := event.get("date"):
                content += f"\n\n**Date**: {date}"

            self.memory.write(
                path=path,
                content=content,
                summary=description[:100],
                tags=["events"],
            )

    def _store_preferences(self, preferences: List[Dict], session_id: str) -> None:
        """Store preferences."""
        if not preferences:
            return

        path = "preferences/user.md"

        try:
            existing = self.memory.read(path)
            # Append new preferences
            new_prefs = "\n".join(f"- {p.get('type', '')}: {p.get('value', '')}" for p in preferences)
            self.memory.update(path, existing + f"\n\n{new_prefs}")
        except FileNotFoundError:
            content = "# User Preferences\n\n" + "\n".join(
                f"- {p.get('type', '')}: {p.get('value', '')}" for p in preferences
            )
            self.memory.write(
                path=path,
                content=content,
                summary="User preferences and habits",
                tags=["preferences"],
            )

    def _append_daily_log(self, turn: Dict, session_id: str) -> None:
        """Append turn to daily log."""
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        path = f"daily/{today}.md"

        entry = f"- {turn['speaker']}: {turn['content'][:200]}"

        try:
            existing = self.memory.read(path)
            self.memory.update(path, existing + f"\n{entry}")
        except FileNotFoundError:
            content = f"# {today}\n\n{entry}"
            self.memory.write(
                path=path,
                content=content,
                summary=f"{today} - Daily log",
                tags=["daily"],
            )
