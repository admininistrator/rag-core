"""Validate repository documentation links, anchors, and task dependencies."""

from __future__ import annotations

import re
import sys
import unicodedata
from collections.abc import Iterable
from os import walk
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".uv-cache",
    ".uv-python",
    ".venv",
    "__pycache__",
}
IGNORED_ROOT_DIRECTORIES = {"backups", "logs", "model-cache", "models", "runtime", "var"}
TASK_FIELDS = (
    "Trạng thái",
    "Phụ thuộc",
    "Tham chiếu kế hoạch",
    "Công việc",
    "Xong khi thỏa mãn DoD",
    "Cạm bẫy",
    "Ghi chú thực thi",
)
VALID_STATUSES = {"TODO", "IN_PROGRESS", "BLOCKED", "COMPLETE"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
HTML_ANCHOR = re.compile(r'<a\s+(?:name|id)="([^"]+)"\s*></a>', re.IGNORECASE)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
TASK_HEADING = re.compile(r"^### (T\d{2}) — (.+)$", re.MULTILINE)


class DocumentationError(ValueError):
    """Raised when repository documentation violates its structural contract."""


def _markdown_files() -> list[Path]:
    files: list[Path] = []
    for current, directories, names in walk(ROOT):
        current_path = Path(current)
        directories[:] = [
            name
            for name in directories
            if not _ignored_directory(current_path / name)
        ]
        files.extend(current_path / name for name in names if name.endswith(".md"))
    return sorted(files)


def _ignored_directory(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path.name in IGNORED_DIRECTORY_NAMES:
        return True
    if len(relative.parts) == 1 and path.name in IGNORED_ROOT_DIRECTORIES:
        return True
    if relative.parts[:2] == ("corpus-documents", ".downloads"):
        return True
    return (
        len(relative.parts) >= 3
        and relative.parts[0] == "corpus-documents"
        and relative.parts[2] in {"documents", "raw"}
    )


def _heading_slug(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value).strip().lower()
    value = unicodedata.normalize("NFC", value)
    value = "".join(char for char in value if char.isalnum() or char in {" ", "-", "_"})
    return re.sub(r"[\s-]+", "-", value).strip("-")


def _anchors(text: str) -> set[str]:
    anchors = set(HTML_ANCHOR.findall(text))
    occurrences: dict[str, int] = {}
    for heading in HEADING.findall(text):
        base = _heading_slug(heading)
        if not base:
            continue
        count = occurrences.get(base, 0)
        occurrences[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def _split_link(target: str) -> tuple[str, str]:
    target = target.strip().strip("<>")
    if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
        return "", ""
    filename, separator, fragment = target.partition("#")
    return unquote(filename), unquote(fragment) if separator else ""


def check_links(files: Iterable[Path]) -> int:
    checked = 0
    cached_text: dict[Path, str] = {}
    for source in files:
        text = cached_text.setdefault(source, source.read_text(encoding="utf-8"))
        for raw_target in MARKDOWN_LINK.findall(text):
            filename, fragment = _split_link(raw_target)
            if not filename and not fragment:
                continue
            target = (source.parent / filename).resolve() if filename else source.resolve()
            try:
                target.relative_to(ROOT)
            except ValueError as exc:
                raise DocumentationError(f"Link escapes repository in {source}: {raw_target}") from exc
            if not target.is_file():
                raise DocumentationError(f"Broken link in {source}: {raw_target}")
            if fragment:
                target_text = cached_text.setdefault(target, target.read_text(encoding="utf-8"))
                if fragment not in _anchors(target_text):
                    raise DocumentationError(f"Missing anchor in {source}: {raw_target}")
            checked += 1
    return checked


def _task_bodies(text: str) -> list[tuple[str, str]]:
    matches = list(TASK_HEADING.finditer(text))
    expected = [f"T{index:02d}" for index in range(37)]
    actual = [match.group(1) for match in matches]
    if actual != expected:
        raise DocumentationError(f"Expected ordered tasks T00-T36; found {actual}")
    return [
        (
            match.group(1),
            text[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(text)],
        )
        for index, match in enumerate(matches)
    ]


def _assert_acyclic(graph: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task: str) -> None:
        if task in visiting:
            raise DocumentationError(f"Dependency cycle includes {task}")
        if task in visited:
            return
        visiting.add(task)
        for dependency in graph[task]:
            visit(dependency)
        visiting.remove(task)
        visited.add(task)

    for task in graph:
        visit(task)


def check_tasks(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    graph: dict[str, list[str]] = {}
    for index, (task, body) in enumerate(_task_bodies(text)):
        for field in TASK_FIELDS:
            if f"**{field}:**" not in body:
                raise DocumentationError(f"Missing task field {field!r} in {task}")
        status_match = re.search(r"\*\*Trạng thái:\*\* (\w+)", body)
        dependency_match = re.search(r"\*\*Phụ thuộc:\*\* ([^\n]+)", body)
        if status_match is None or status_match.group(1) not in VALID_STATUSES:
            raise DocumentationError(f"Invalid status in {task}")
        if dependency_match is None:
            raise DocumentationError(f"Missing dependency value in {task}")
        dependencies = re.findall(r"T\d{2}", dependency_match.group(1))
        unknown = [dependency for dependency in dependencies if dependency not in {f"T{i:02d}" for i in range(37)}]
        if unknown:
            raise DocumentationError(f"Unknown dependencies in {task}: {unknown}")
        if any(int(dependency[1:]) >= index for dependency in dependencies):
            raise DocumentationError(f"Dependency must precede {task}: {dependencies}")
        if index and f"T{index - 1:02d}" not in dependencies:
            raise DocumentationError(f"Sequential predecessor missing from {task}")
        graph[task] = dependencies
    _assert_acyclic(graph)
    return len(graph), sum(len(dependencies) for dependencies in graph.values())


def main() -> int:
    try:
        files = _markdown_files()
        for path in files:
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise DocumentationError(f"Empty Markdown file: {path}")
            if "\ufffd" in text:
                raise DocumentationError(f"Unicode replacement character in {path}")
        link_count = check_links(files)
        task_count, edge_count = check_tasks(ROOT / "docs" / "tasks.md")
    except (DocumentationError, UnicodeDecodeError) as exc:
        print(f"DOCUMENTATION CHECK: FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"PASS UTF-8/nonempty Markdown: {len(files)} files")
    print(f"PASS internal links/anchors: {link_count}")
    print(f"PASS task fields/status/dependencies: {task_count} tasks, {edge_count} edges, acyclic")
    print("DOCUMENTATION CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
