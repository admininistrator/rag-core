"""Office text/tables and strict UTF-8 CSV; values are data, never executable code."""

import csv
import io
import zipfile
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

from rag_core.contracts.v1 import CsvLocator, PptxLocator, XlsxLocator
from rag_core.domain.documents import Block, ParseError, ParserLimits, TableCell

from .archive import package_target
from .tables import table_rows, table_text


class BlockBuffer:
    def __init__(self, limits: ParserLimits) -> None:
        self.limits = limits
        self.blocks: list[Block] = []
        self.chars = 0

    def add(self, block: Block) -> None:
        self.chars += len(block.text)
        if len(self.blocks) >= self.limits.max_blocks or self.chars > self.limits.max_text_chars:
            raise ParseError("extraction_limit")
        self.blocks.append(block)


def stored_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return str(value)


def xlsx_blocks(path: Path, limits: ParserLimits) -> tuple[list[Block], tuple[str, ...]]:
    from defusedxml.ElementTree import fromstring  # type: ignore[import-untyped]
    from openpyxl import load_workbook  # type: ignore[import-untyped]
    from openpyxl.utils.cell import get_column_letter  # type: ignore[import-untyped]

    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    parts: dict[str, str] = {}
    caches: dict[str, set[str]] = {}
    with zipfile.ZipFile(path) as archive:
        rels = fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.attrib["Id"]: package_target("xl/workbook.xml", rel.attrib["Target"])
            for rel in rels
            if rel.attrib.get("TargetMode") != "External"
        }
        root = fromstring(archive.read("xl/workbook.xml"))
        for sheet in root.findall("s:sheets/s:sheet", ns):
            part = targets.get(sheet.attrib[rel_ns])
            if part is None:
                raise ParseError("corrupt_document")
            parts[sheet.attrib["name"]] = part
            xml = fromstring(archive.read(part))
            caches[part] = {
                cell.attrib["r"]
                for cell in xml.findall("s:sheetData/s:row/s:c", ns)
                if cell.find("s:f", ns) is not None
                and (cached := cell.find("s:v", ns)) is not None
                and (cached.text is not None or cell.attrib.get("t") == "str")
            }

    # No Excel automation, recalculation, VBA, external workbook loading or save.
    formulas = load_workbook(path, data_only=False, keep_vba=False, keep_links=False)
    values = load_workbook(path, data_only=True, keep_vba=False, keep_links=False)
    buffer = BlockBuffer(limits)
    warnings: set[str] = set()
    try:
        if len(formulas.sheetnames) > limits.max_sheets:
            raise ParseError("sheet_limit")
        if len(formulas.worksheets) != len(formulas.sheetnames):
            warnings.add("chartsheets_not_extracted")
        for sheet in formulas.worksheets:
            part = parts[sheet.title]
            value_sheet = values[sheet.title]
            # Sparse source cells, not the potentially forged worksheet dimension.
            actual = [cell for cell in sheet._cells.values() if cell.value is not None]
            if not actual:
                continue
            regions = tuple(sheet.merged_cells.ranges)
            min_row = min([cell.row for cell in actual] + [region.min_row for region in regions])
            max_row = max([cell.row for cell in actual] + [region.max_row for region in regions])
            min_col = min([cell.column for cell in actual] + [region.min_col for region in regions])
            max_col = max([cell.column for cell in actual] + [region.max_col for region in regions])
            if (max_row - min_row + 1) * (max_col - min_col + 1) > limits.max_table_cells:
                raise ParseError("table_limit")
            merged: dict[tuple[int, int], str] = {}
            for region in regions:
                anchor = f"{get_column_letter(region.min_col)}{region.min_row}"
                for row in range(region.min_row, region.max_row + 1):
                    for column in range(region.min_col, region.max_col + 1):
                        merged[row, column] = anchor
            # Header context is the leading text-only rows of each blank-separated region.
            # It is preserved as source context, not a claim about semantic header detection.
            headers: list[tuple[str, ...]] = []
            header_phase = True
            normalized_values: dict[str, str] = {}
            for row in sheet.iter_rows(
                min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col
            ):
                if all(cell.value is None for cell in row):
                    headers = []
                    header_phase = True
                    continue
                cells = []
                numeric = False
                for cell in row:
                    formula = None
                    origin = "stored"
                    value = cell.value
                    if cell.data_type == "f":
                        formula = value if isinstance(value, str) else getattr(value, "text", None)
                        if not isinstance(formula, str):
                            raise ParseError("unsupported_formula")
                        if cell.coordinate in caches[part]:
                            value = value_sheet[cell.coordinate].value
                            origin = "formula_cache"
                            warnings.add("formula_cached_values_unverified")
                        else:
                            value = "[formula cache unavailable]"
                            origin = "missing_formula_cache"
                            warnings.add("formula_cache_missing")
                        numeric = True
                    numeric |= cell.data_type in {"n", "d", "b"} and cell.value is not None
                    cells.append(
                        TableCell(
                            reference=cell.coordinate,
                            value=stored_text(value),
                            formula=formula,
                            value_origin=origin,
                            number_format=cell.number_format,
                            merged_origin=merged.get((cell.row, cell.column)),
                        )
                    )
                row_values = tuple(cell.value for cell in cells)
                normalized_values.update((cell.reference, cell.value) for cell in cells)
                if header_phase and (not headers or not numeric):
                    headers.append(
                        tuple(
                            normalized_values.get(cell.merged_origin, cell.value)
                            if cell.merged_origin
                            else cell.value
                            for cell in cells
                        )
                    )
                else:
                    header_phase = False
                context = table_rows(headers)
                text = (
                    table_text((*context, row_values))
                    if context != (row_values,)
                    else table_text(context)
                )
                formats = [
                    f"{cell.reference}={cell.number_format}"
                    for cell in cells
                    if cell.value and cell.number_format != "General"
                ]
                if formats:
                    text += "\nExcel number formats (stored values, not rendered): " + "; ".join(
                        formats
                    )
                if any(cell.formula for cell in cells):
                    text += (
                        "\nFormula results are stored caches only; not recalculated or verified."
                    )
                buffer.add(
                    Block(
                        kind="table",
                        text=text,
                        rows=(row_values,),
                        table_headers=context,
                        cells=tuple(cells),
                        heading_path=(sheet.title,),
                        source_part=part,
                        source_path=f"/s:worksheet/s:sheetData/s:row[@r='{row[0].row}']",
                        locator=XlsxLocator(
                            kind="xlsx",
                            sheet=sheet.title,
                            cell_range=f"{row[0].coordinate}:{row[-1].coordinate}",
                            headers=[table_text((header,)) for header in context if any(header)],
                        ),
                    )
                )
    finally:
        formulas.close()
        values.close()
    return buffer.blocks, tuple(sorted(warnings))


def csv_blocks(text: str, limits: ParserLimits) -> list[Block]:
    text = text.removeprefix("\ufeff")
    csv.field_size_limit(limits.max_text_chars)
    # Sniffer handles quoted delimiter/newline data; strict parsing validates full input.
    try:
        dialect = csv.Sniffer().sniff(text[:65536], delimiters=",;\t|")
        delimiter = dialect.delimiter
    except csv.Error:
        # A single column is supported; ambiguous multi-column data is refused.
        if any(char in text for char in ",;\t|"):
            raise ParseError("invalid_csv") from None
        delimiter = ","
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter, strict=True)
    buffer = BlockBuffer(limits)
    headers: tuple[str, ...] | None = None
    count = 0
    try:
        for index, row in enumerate(reader, 1):
            if not row:
                raise ParseError("invalid_csv")
            if headers is None:
                headers = tuple(row)
            if len(row) != len(headers):
                raise ParseError("invalid_csv")
            count += len(row)
            if count > limits.max_table_cells:
                raise ParseError("table_limit")
            columns = [
                value if value.strip() else f"Column {n}" for n, value in enumerate(headers, 1)
            ]
            rows = table_rows((row,))
            context = (headers,)
            evidence = table_text(rows if index == 1 else (*context, *rows))
            buffer.add(
                Block(
                    kind="table",
                    rows=rows,
                    table_headers=context,
                    text=evidence or "[empty CSV fields]",
                    locator=CsvLocator(kind="csv", row_start=index, row_end=index, columns=columns),
                    source_path=f"record[{index}]",
                )
            )
    except csv.Error as exc:
        code = "extraction_limit" if "field larger than field limit" in str(exc) else "invalid_csv"
        raise ParseError(code) from None
    if not any(value.strip() for block in buffer.blocks for row in block.rows for value in row):
        raise ParseError("empty_extraction")
    return buffer.blocks


def pptx_blocks(path: Path, limits: ParserLimits) -> tuple[list[Block], tuple[str, ...]]:
    from pptx import Presentation
    from pptx.shapes.group import GroupShape

    presentation = Presentation(str(path))
    if len(presentation.slides) > limits.max_slides:
        raise ParseError("slide_limit")
    buffer = BlockBuffer(limits)
    warnings: set[str] = set()
    cell_count = 0

    def visit(
        shape: Any, slide: int, index: int, part: str, title: tuple[str, ...], start: int = 0
    ) -> int:
        nonlocal cell_count
        if isinstance(shape, GroupShape):
            for child in shape.shapes:
                start = visit(child, slide, index, part, title, start)
            return start
        if shape.has_table:
            rows = table_rows(tuple(cell.text for cell in row.cells) for row in shape.table.rows)
            cell_count += sum(len(row) for row in rows)
            if cell_count > limits.max_table_cells:
                raise ParseError("table_limit")
            if table_text(rows).strip():
                buffer.add(
                    Block(
                        kind="table",
                        text=table_text(rows),
                        rows=rows,
                        table_headers=rows[:1],
                        heading_path=title,
                        source_part=part,
                        source_path=shape.element.getroottree().getpath(shape.element),
                        locator=PptxLocator(kind="pptx", slide=slide, shape=index, block=start),
                    )
                )
            return start + 1
        elif shape.has_text_frame:
            for block, paragraph in enumerate(shape.text_frame.paragraphs):
                if paragraph.text.strip():
                    buffer.add(
                        Block(
                            kind="paragraph",
                            text=paragraph.text,
                            heading_path=title,
                            source_part=part,
                            source_path=paragraph._p.getroottree().getpath(paragraph._p),
                            locator=PptxLocator(
                                kind="pptx", slide=slide, shape=index, block=start + block
                            ),
                        )
                    )
            return start + len(shape.text_frame.paragraphs)
        else:
            warnings.add("non_text_shapes_not_extracted")
            return start

    for number, slide in enumerate(presentation.slides, 1):
        part = str(slide.part.partname).lstrip("/")
        title = (slide.shapes.title.text,) if slide.shapes.title and slide.shapes.title.text else ()
        for index, shape in enumerate(slide.shapes):
            visit(shape, number, index, part, title)
    return buffer.blocks, tuple(sorted(warnings))
