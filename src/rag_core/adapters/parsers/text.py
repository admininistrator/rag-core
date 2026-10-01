"""UTF-8/Markdown and non-rendering HTML extraction; no network or execution."""

import re
from html.parser import HTMLParser

from rag_core.contracts.v1 import HtmlLocator, OffsetRange, TextLocator
from rag_core.domain.documents import Block, ParseError


def decode(data: bytes) -> str:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ParseError("invalid_encoding") from None
    if any(ord(char) < 32 and char not in "\t\n\r\f" for char in text):
        raise ParseError("mime_mismatch")
    return text


def text_blocks(text: str, markdown: bool) -> list[Block]:
    lines = text.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    headings: list[tuple[int, str]] = []
    blocks: list[Block] = []
    index = 0
    while index < len(lines):
        if not lines[index].strip("\ufeff \t\r\n"):
            index += 1
            continue
        first = index
        raw = lines[index].lstrip("\ufeff")
        heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$", raw) if markdown else None
        setext = (
            markdown
            and index + 1 < len(lines)
            and re.fullmatch(r" {0,3}(=+|-+)\s*", lines[index + 1])
        )
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})", raw) if markdown else None
        kind = "paragraph"
        if heading or (setext and not fence):
            level = len(heading[1]) if heading else (1 if "=" in lines[index + 1] else 2)
            title = heading[2] if heading else raw.strip()
            headings = [(n, value) for n, value in headings if n < level]
            headings.append((level, title))
            kind = "heading"
            index += 1 if heading else 2
        elif fence:
            kind = "code"
            index += 1
            while index < len(lines):
                closing = re.match(r"^ {0,3}(\`+|~+)\s*$", lines[index])
                index += 1
                if closing and closing[1][0] == fence[1][0] and len(closing[1]) >= len(fence[1]):
                    break
        else:
            index += 1
            while index < len(lines) and lines[index].strip():
                if markdown and re.match(r"^ {0,3}(#{1,6}\s|`{3,}|~{3,})", lines[index]):
                    break
                index += 1
        start, end = starts[first], starts[index]
        while start < end and text[start] in "\ufeff \t\r\n":
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        value = text[start:end]
        rows: tuple[tuple[str, ...], ...] = ()
        if markdown and kind == "paragraph":
            table_lines = value.splitlines()
            if (
                len(table_lines) >= 2
                and "|" in table_lines[0]
                and all(
                    re.fullmatch(r":?-{3,}:?", cell.strip())
                    for cell in table_lines[1].strip().strip("|").split("|")
                )
            ):
                kind = "table"
                rows = tuple(
                    tuple(cell.strip() for cell in row.strip().strip("|").split("|"))
                    for row in (table_lines[:1] + table_lines[2:])
                )
        blocks.append(
            Block(
                kind=kind,
                text=value,
                heading_path=tuple(value for _, value in headings),
                locator=TextLocator(
                    kind="md" if markdown else "txt",
                    line_start=first + 1,
                    line_end=index,
                    paragraph=len(blocks),
                    offsets=OffsetRange(start=start, end=end),
                ),
                rows=rows,
            )
        )
    return blocks


class SafeHTML(HTMLParser):
    """Offsets refer to original HTML characters, including tags/entities in the span."""

    hidden = frozenset({"script", "style", "template", "noscript", "iframe", "object", "svg"})
    boundaries = frozenset(
        {
            "p",
            "div",
            "li",
            "pre",
            "blockquote",
            "section",
            "article",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "table",
        }
    )

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=True)
        self.text = text
        self.starts = [0]
        for match in re.finditer("\n", text):
            self.starts.append(match.end())
        self.blocks: list[Block] = []
        self.headings: list[tuple[int, str]] = []
        self.parts: list[str] = []
        self.start = 0
        self.tag = "p"
        self.ignored: list[str] = []
        self.table_rows: list[list[str]] | None = None
        self.cell: list[str] | None = None

    def position(self) -> int:
        line, column = self.getpos()
        return self.starts[line - 1] + column

    def flush(self, end: int) -> None:
        value = "".join(self.parts).strip()
        self.parts = []
        if not value:
            return
        kind = "code" if self.tag == "pre" else "paragraph"
        if re.fullmatch(r"h[1-6]", self.tag):
            level = int(self.tag[1])
            self.headings = [(n, title) for n, title in self.headings if n < level]
            self.headings.append((level, value))
            kind = "heading"
        self.blocks.append(
            Block(
                kind=kind,
                text=value,
                heading_path=tuple(title for _, title in self.headings),
                locator=HtmlLocator(
                    kind="html",
                    block=len(self.blocks),
                    heading_path=[title for _, title in self.headings],
                    offsets=OffsetRange(start=self.start, end=max(end, self.start + 1)),
                ),
            )
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.hidden:
            if not self.ignored:
                self.flush(self.position())
            self.ignored.append(tag)
            return
        if self.ignored:
            return
        if tag == "table" and self.table_rows is None:
            self.flush(self.position())
            self.start = self.position()
            self.table_rows = []
        elif self.table_rows is not None:
            if tag == "tr":
                self.table_rows.append([])
            elif tag in {"td", "th"}:
                self.cell = []
        elif tag in self.boundaries:
            self.flush(self.position())
            self.start = self.position()
            self.tag = tag
        elif tag == "br":
            self.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        end = self.text.find(">", self.position()) + 1
        if self.ignored:
            if tag == self.ignored[-1]:
                self.ignored.pop()
                self.start = end
            return
        if self.table_rows is not None:
            if tag in {"td", "th"} and self.cell is not None:
                if not self.table_rows:
                    self.table_rows.append([])
                self.table_rows[-1].append("".join(self.cell).strip())
                self.cell = None
            elif tag == "table":
                rows = tuple(tuple(row) for row in self.table_rows)
                self.table_rows = None
                value = "\n".join("\t".join(row) for row in rows)
                if value.strip():
                    self.blocks.append(
                        Block(
                            kind="table",
                            text=value,
                            rows=rows,
                            heading_path=tuple(title for _, title in self.headings),
                            locator=HtmlLocator(
                                kind="html",
                                block=len(self.blocks),
                                heading_path=[title for _, title in self.headings],
                                offsets=OffsetRange(start=self.start, end=end),
                            ),
                        )
                    )
                self.start = end
        elif tag in self.boundaries:
            self.flush(end)
            self.start = end
            self.tag = "p"

    def handle_data(self, data: str) -> None:
        if self.ignored:
            return
        if self.table_rows is not None:
            if self.cell is not None:
                self.cell.append(data)
        else:
            if not self.parts:
                self.start = self.position()
            self.parts.append(data)

    def finish(self) -> list[Block]:
        self.feed(self.text)
        self.close()
        if self.table_rows is not None:
            raise ParseError("corrupt_document")
        self.flush(len(self.text))
        return self.blocks
