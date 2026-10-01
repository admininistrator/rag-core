"""OOXML preflight: bounded CRC/XML validation, no extraction or external requests."""

import posixpath
import re
import zipfile
from pathlib import Path, PurePosixPath

from rag_core.domain.documents import ParseError, ParserLimits

MAIN_PARTS = {
    "docx": ("word/document.xml", "wordprocessingml.document"),
    "xlsx": ("xl/workbook.xml", "spreadsheetml.sheet"),
    "pptx": ("ppt/presentation.xml", "presentationml.presentation"),
}


def package_target(part: str, target: str) -> str:
    name = posixpath.normpath(posixpath.join(posixpath.dirname(part), target))
    if target.startswith("/"):
        name = posixpath.normpath(target.lstrip("/"))
    if name.startswith("../") or name == ".." or "\\" in name or ":" in name:
        raise ParseError("unsafe_archive")
    return name


def cell_position(reference: str) -> tuple[int, int]:
    match = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]*)", reference)
    if match is None:
        raise ParseError("corrupt_document")
    column = 0
    for letter in match[1]:
        column = column * 26 + ord(letter) - ord("A") + 1
    row = int(match[2])
    if column > 16384 or row > 1048576:
        raise ParseError("corrupt_document")
    return row, column


def archive_preflight(path: Path, limits: ParserLimits, format_: str = "docx") -> bool:
    from defusedxml.ElementTree import fromstring  # type: ignore[import-untyped]

    external = False
    main, type_name = MAIN_PARTS[format_]
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > limits.max_archive_entries:
            raise ParseError("archive_limit")
        if len({entry.filename for entry in entries}) != len(entries):
            raise ParseError("corrupt_document")
        total = 0
        for entry in entries:
            name = entry.filename
            if (
                PurePosixPath(name).is_absolute()
                or ".." in PurePosixPath(name).parts
                or "\\" in name
                or ":" in name
            ):
                raise ParseError("unsafe_archive")
            if entry.flag_bits & 1:
                raise ParseError("encrypted_document")
            total += entry.file_size
            if (
                total > limits.max_expanded_bytes
                or entry.file_size > max(entry.compress_size, 1) * limits.max_compression_ratio
            ):
                raise ParseError("archive_limit")
            if "vbaproject" in name.lower():
                raise ParseError("unsafe_archive")
        if "[Content_Types].xml" not in archive.namelist() or main not in archive.namelist():
            raise ParseError("mime_mismatch")
        cells = 0
        merged_cells = 0
        sheet_area = 0
        for entry in entries:
            data = archive.read(entry)  # CRC checked; no package member written to disk
            if not entry.filename.endswith((".xml", ".rels")):
                continue
            root = fromstring(data, forbid_dtd=True, forbid_entities=True, forbid_external=True)
            if entry.filename == "[Content_Types].xml":
                expected = f"application/vnd.openxmlformats-officedocument.{type_name}.main+xml"
                if any(
                    "macroenabled" in item.attrib.get("ContentType", "").lower() for item in root
                ):
                    raise ParseError("unsafe_archive")
                if not any(
                    item.attrib.get("ContentType") == expected
                    and item.attrib.get("PartName") == "/" + main
                    for item in root
                ):
                    raise ParseError("mime_mismatch")
            if entry.filename.endswith(".rels"):
                part = entry.filename.replace("/_rels/", "/").removesuffix(".rels")
                if part == "_rels/":
                    part = ""
                for item in root:
                    if item.attrib.get("TargetMode") == "External":
                        external = True
                    elif target := item.attrib.get("Target"):
                        package_target(part, target)
            if format_ == "xlsx" and entry.filename.startswith("xl/worksheets/"):
                positions = []
                references: set[str] = set()
                for item in root.iter():
                    tag = item.tag.rsplit("}", 1)[-1]
                    if tag == "c":
                        if item.attrib["r"] in references:
                            raise ParseError("corrupt_document")
                        references.add(item.attrib["r"])
                        positions.append(cell_position(item.attrib["r"]))
                        cells += 1
                    elif tag == "mergeCell":
                        ends = item.attrib["ref"].split(":")
                        if len(ends) not in {1, 2}:
                            raise ParseError("corrupt_document")
                        start, end = cell_position(ends[0]), cell_position(ends[-1])
                        if start[0] > end[0] or start[1] > end[1]:
                            raise ParseError("corrupt_document")
                        positions.extend((start, end))
                        merged_cells += (end[0] - start[0] + 1) * (end[1] - start[1] + 1)
                if positions:
                    rows, columns = zip(*positions, strict=True)
                    area = (max(rows) - min(rows) + 1) * (max(columns) - min(columns) + 1)
                    sheet_area += area
                if max(cells, merged_cells, sheet_area) > limits.max_table_cells:
                    raise ParseError("table_limit")
            elif format_ in {"pptx", "docx"}:
                cells += sum(item.tag.rsplit("}", 1)[-1] == "tc" for item in root.iter())
                if cells > limits.max_table_cells:
                    raise ParseError("table_limit")
            if entry.filename == main:
                tag = "sheet" if format_ == "xlsx" else "sldId"
                count = sum(item.tag.rsplit("}", 1)[-1] == tag for item in root.iter())
                if format_ == "xlsx" and count > limits.max_sheets:
                    raise ParseError("sheet_limit")
                if format_ == "pptx" and count > limits.max_slides:
                    raise ParseError("slide_limit")
    return external
