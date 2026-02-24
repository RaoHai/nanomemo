"""NanoMemo - Structured long-term memory for AI agents."""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class SearchResult:
    """Result from memory search."""

    path: str
    summary: str
    tags: List[str]
    created: str
    updated: Optional[str] = None


class Memory:
    """
    NanoMemo memory manager.

    Provides operations for searching, reading, and writing structured memory files.
    """

    def __init__(self, base_path: str | Path):
        """
        Initialize memory with base directory path.

        Args:
            base_path: Path to memory directory
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def search_summaries(
        self, query: str, case_sensitive: bool = False
    ) -> List[SearchResult]:
        """
        Search memory file summaries for query string.

        Args:
            query: Search query
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of search results
        """
        cmd = [
            "rg",
            f"^summary:.*{query}",
            str(self.base_path),
            "--no-ignore",
            "--hidden",
            "-n",  # Show line numbers
        ]
        if not case_sensitive:
            cmd.append("-i")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return []

            return self._parse_search_results(result.stdout)
        except FileNotFoundError:
            raise RuntimeError(
                "ripgrep (rg) not found. Install it: https://github.com/BurntSushi/ripgrep"
            )

    def search_tags(self, tag: str) -> List[SearchResult]:
        """
        Search memory files by tag.

        Args:
            tag: Tag to search for

        Returns:
            List of search results
        """
        cmd = [
            "rg",
            f"^tags:.*{tag}",
            str(self.base_path),
            "--no-ignore",
            "--hidden",
            "-n",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return []

            return self._parse_search_results(result.stdout)
        except FileNotFoundError:
            raise RuntimeError("ripgrep (rg) not found")

    def search_content(
        self, query: str, case_sensitive: bool = False
    ) -> List[SearchResult]:
        """
        Full-text search across all memory files.

        Args:
            query: Search query
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of search results
        """
        cmd = [
            "rg",
            query,
            str(self.base_path),
            "--no-ignore",
            "--hidden",
            "-l",  # Files with matches only
        ]
        if not case_sensitive:
            cmd.append("-i")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return []

            files = result.stdout.strip().split("\n")
            results = []
            for file_path in files:
                if file_path:
                    try:
                        metadata = self.get_metadata(file_path)
                        results.append(
                            SearchResult(
                                path=str(
                                    Path(file_path).relative_to(self.base_path)
                                ),
                                summary=metadata.get("summary", ""),
                                tags=metadata.get("tags", []),
                                created=metadata.get("created", ""),
                                updated=metadata.get("updated"),
                            )
                        )
                    except Exception:
                        continue
            return results
        except FileNotFoundError:
            raise RuntimeError("ripgrep (rg) not found")

    def read(self, path: str) -> str:
        """
        Read a memory file.

        Args:
            path: Relative path to memory file

        Returns:
            File contents

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        full_path = self.base_path / path
        return full_path.read_text(encoding="utf-8")

    def write(
        self,
        path: str,
        content: str,
        summary: str,
        tags: Optional[List[str]] = None,
        related: Optional[List[str]] = None,
        status: Optional[str] = None,
    ) -> None:
        """
        Write a memory file with frontmatter.

        Args:
            path: Relative path to memory file
            content: File content (without frontmatter)
            summary: One-line summary for frontmatter
            tags: Optional list of tags
            related: Optional list of related file paths
            status: Optional status (in-progress, resolved, blocked, abandoned)
        """
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        frontmatter: Dict[str, Any] = {
            "summary": summary,
            "created": datetime.now().strftime("%Y-%m-%d"),
        }

        if tags:
            frontmatter["tags"] = tags
        if related:
            frontmatter["related"] = related
        if status:
            frontmatter["status"] = status

        frontmatter_str = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True
        )
        full_content = f"---\n{frontmatter_str}---\n\n{content}"

        full_path.write_text(full_content, encoding="utf-8")

    def update(self, path: str, content: str, update_timestamp: bool = True) -> None:
        """
        Update an existing memory file.

        Args:
            path: Relative path to memory file
            content: New content (without frontmatter)
            update_timestamp: Whether to update the 'updated' field in frontmatter
        """
        full_path = self.base_path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Memory file not found: {path}")

        # Extract existing frontmatter
        existing_content = full_path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", existing_content, re.DOTALL)

        if not match:
            raise ValueError(f"Invalid frontmatter in file: {path}")

        frontmatter_str, _ = match.groups()
        frontmatter = yaml.safe_load(frontmatter_str)

        if update_timestamp:
            frontmatter["updated"] = datetime.now().strftime("%Y-%m-%d")

        new_frontmatter_str = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True
        )
        full_content = f"---\n{new_frontmatter_str}---\n\n{content}"

        full_path.write_text(full_content, encoding="utf-8")

    def delete(self, path: str) -> None:
        """
        Delete a memory file.

        Args:
            path: Relative path to memory file
        """
        full_path = self.base_path / path
        full_path.unlink()

    def list_category(self, category: str) -> List[str]:
        """
        List all files in a category.

        Args:
            category: Category name (e.g., 'people', 'projects')

        Returns:
            List of relative file paths
        """
        category_path = self.base_path / category
        if not category_path.exists():
            return []

        files = []
        for file_path in category_path.rglob("*.md"):
            files.append(str(file_path.relative_to(self.base_path)))

        return sorted(files)

    def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Extract frontmatter metadata from a memory file.

        Args:
            path: Relative path to memory file

        Returns:
            Dictionary of frontmatter fields

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If frontmatter is invalid
        """
        content = self.read(path)
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)

        if not match:
            raise ValueError(f"Invalid frontmatter in file: {path}")

        frontmatter_str = match.group(1)
        return yaml.safe_load(frontmatter_str)

    def _parse_search_results(self, rg_output: str) -> List[SearchResult]:
        """Parse ripgrep output into SearchResult objects."""
        results = []
        for line in rg_output.strip().split("\n"):
            if not line:
                continue

            # Format: path:line_number:content
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue

            file_path = parts[0]
            try:
                metadata = self.get_metadata(file_path)
                results.append(
                    SearchResult(
                        path=str(Path(file_path).relative_to(self.base_path)),
                        summary=metadata.get("summary", ""),
                        tags=metadata.get("tags", []),
                        created=metadata.get("created", ""),
                        updated=metadata.get("updated"),
                    )
                )
            except Exception:
                continue

        return results


__all__ = ["Memory", "SearchResult"]
