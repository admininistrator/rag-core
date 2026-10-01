"""Docling's CPU OCR stage only: no layout pipeline, network or model downloads."""

import math
import subprocess
import sys
import time
from pathlib import Path
from typing import cast

from rag_core.contracts.v1 import BoundingBox, ImageLocator, OffsetRange, PdfLocator
from rag_core.domain.documents import Block, OcrConfig, OcrReport, ParseError, ParserLimits


def ocr_blocks(
    path: Path,
    pages: tuple[int, ...],
    limits: ParserLimits,
    config: OcrConfig,
    *,
    image: bool = False,
    labels: list[str] | None = None,
    image_id: str = "",
) -> tuple[list[Block], tuple[int, ...], OcrReport]:
    from docling.backend.image_backend import ImageDocumentBackend
    from docling.backend.pdf_backend import PdfDocumentBackend
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.base_models import InputFormat, Page
    from docling.datamodel.document import ConversionResult, InputDocument
    from docling.datamodel.pipeline_options import OcrMode, TesseractCliOcrOptions
    from docling.models.stages.ocr.tesseract_ocr_cli_model import TesseractOcrCliModel
    from pandas import DataFrame  # type: ignore[import-untyped]  # upstream lacks stubs

    started = time.monotonic()
    try:
        probe = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        if not {"eng", "vie"}.issubset(set(probe.stdout.decode("utf-8").splitlines()[1:])):
            raise ParseError("ocr_tessdata_missing")
    except FileNotFoundError:
        raise ParseError("ocr_engine_missing") from None
    except (OSError, subprocess.SubprocessError):
        raise ParseError("ocr_tessdata_missing") from None

    class StrictTesseract(TesseractOcrCliModel):
        # Upstream swallows CLI failure into empty cells. Preserve technical errors.
        def _run_tesseract(self, ifilename: str, osd: DataFrame | None) -> DataFrame:
            try:
                return super()._run_tesseract(ifilename, osd)
            except (OSError, subprocess.SubprocessError):
                raise ParseError("ocr_failed") from None

    try:
        model = StrictTesseract(
            enabled=True,
            artifacts_path=None,
            options=TesseractCliOcrOptions(
                lang=["vie", "eng"],
                mode=OcrMode.FULL_PAGE,
                scale=1 if image else 3,
                psm=3,
                path=str(config.tessdata_path.resolve()) if config.tessdata_path else None,
            ),
            accelerator_options=AcceleratorOptions(device=AcceleratorDevice.CPU, num_threads=1),
        )
    except Exception:
        raise ParseError("ocr_tessdata_missing") from None

    input_doc = InputDocument(
        path,
        format=InputFormat.IMAGE if image else InputFormat.PDF,
        backend=ImageDocumentBackend if image else PyPdfiumDocumentBackend,
    )
    if not input_doc.valid:
        raise ParseError("corrupt_document")
    backend = cast(PdfDocumentBackend, input_doc._backend)
    result = ConversionResult(input=input_doc)
    blocks: list[Block] = []
    failed: list[int] = []
    completed: list[int] = []
    total_chars = 0
    try:
        for number in pages:
            page_backend = backend.load_page(number - 1)
            try:
                size = page_backend.get_size()
                # PDFium renders at 1.5x before resize; bound that allocation too.
                factor = 1 if image else 4.5
                if (
                    math.ceil(size.width * factor) * math.ceil(size.height * factor)
                    > limits.max_image_pixels
                ):
                    raise ParseError("image_limit")
                page = Page(page_no=number - 1, size=size)
                page._backend = page_backend
                list(model(result, [page]))
                offset = 0
                found = False
                for index, cell in enumerate(page.cells):
                    value = cell.text.strip()
                    if not value:
                        continue
                    rect = cell.rect.to_bounding_box().to_top_left_origin(size.height)
                    box = (float(rect.l), float(rect.t), float(rect.r), float(rect.b))
                    locator: ImageLocator | PdfLocator
                    if image:
                        locator = ImageLocator(
                            kind="image",
                            image_id=image_id,
                            ocr_block=index,
                            bbox=BoundingBox(x0=box[0], y0=box[1], x1=box[2], y1=box[3]),
                        )
                    else:
                        locator = PdfLocator(
                            kind="pdf",
                            page=number,
                            block=index,
                            printed_page_label=labels[number - 1] if labels else None,
                            offsets=OffsetRange(start=offset, end=offset + len(value)),
                        )
                    blocks.append(
                        Block(
                            kind="paragraph",
                            text=value,
                            locator=locator,
                            bbox=box,
                            extraction_method="ocr",
                        )
                    )
                    found = True
                    offset += len(value) + 1
                    total_chars += len(value)
                    if len(blocks) > limits.max_blocks or total_chars > limits.max_text_chars:
                        raise ParseError("extraction_limit")
                if found:
                    completed.append(number)
                else:
                    failed.append(number)
            finally:
                page_backend.unload()  # type: ignore[no-untyped-call]  # upstream API
    finally:
        backend.unload()  # type: ignore[no-untyped-call]  # upstream API
    parser_rss = child_rss = None
    if sys.platform == "linux":
        import resource

        parser_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        child_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
    return (
        blocks,
        tuple(failed),
        OcrReport(
            engine_version=model._get_name_and_version()[1],
            attempted_pages=pages,
            completed_pages=tuple(completed),
            elapsed_seconds=time.monotonic() - started,
            parser_peak_rss_mib=parser_rss,
            child_peak_rss_mib=child_rss,
        ),
    )


def prepare_image(path: Path, limits: ParserLimits) -> Path:
    """Check dimensions before decoding; normalize to raw pixels, strip EXIF/DPI."""
    from PIL import Image

    with Image.open(path) as image:
        expected = "PNG" if path.suffix.lower() == ".png" else "JPEG"
        if image.format != expected:
            raise ParseError("mime_mismatch")
        if (
            getattr(image, "n_frames", 1) != 1
            or image.width * image.height > limits.max_image_pixels
        ):
            raise ParseError("image_limit")
        target = path.parent / "ocr-image.png"
        with image.convert("RGB") as normalized:
            normalized.info.clear()
            normalized.save(target)
    return target
