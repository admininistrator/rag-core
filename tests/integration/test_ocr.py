"""Actual Docling/Tesseract in the Linux worker image; original synthetic fixtures."""

import hashlib
import json
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import UUID

import pytest
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from test_text_parsers import pdf

from rag_core.adapters.parsers import ParserRegistry
from rag_core.adapters.parsers.registry import FORMATS
from rag_core.domain.documents import (
    OcrConfig,
    ParsedDocument,
    ParseError,
    ParserLimits,
    SourceIdentity,
)

pytestmark = pytest.mark.integration
EN = "First quarter revenue was 120 million VND."
VI = "Doanh thu quý một đạt 120 triệu đồng."


@pytest.fixture(scope="session", autouse=True)
def acceptance_resources():
    started = time.monotonic()
    yield
    peak = Path("/sys/fs/cgroup/memory.peak")
    assert peak.is_file(), "Docker cgroup v2 memory measurement required"
    print(
        f"ACTUAL worker acceptance wall={time.monotonic() - started:.3f}s "
        f"container_memory_peak_mib={int(peak.read_text()) / 1024**2:.3f}"
    )


@pytest.fixture(autouse=True)
def worker_environment() -> None:
    # Missing prerequisites FAIL, never skip OCR acceptance.
    assert sys.platform == "linux", "Run T15 acceptance inside docker/worker.Dockerfile ocr-test"
    assert shutil.which("tesseract")


def image(path: Path, text: str = VI, size: tuple[int, int] = (1800, 420)) -> None:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    with Image.new("RGB", size, "white") as bitmap:
        ImageDraw.Draw(bitmap).text((65, 100), text, font=font, fill="black")
        bitmap.save(path)


def identity(path: Path) -> SourceIdentity:
    return SourceIdentity(
        document_id=UUID(int=15),
        version_id=UUID(int=1),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def parse(
    path: Path,
    *,
    limits: ParserLimits | None = None,
    ocr: OcrConfig | None = None,
    cancel: threading.Event | None = None,
) -> ParsedDocument:
    before = path.read_bytes()
    sandbox = path.parent / "sandbox"
    try:
        return ParserRegistry(sandbox, limits, ocr=ocr or OcrConfig(enabled=True)).parse(
            path,
            filename=path.name,
            content_type=FORMATS[path.suffix][1],
            source=identity(path),
            cancel=cancel,
        )
    finally:
        assert path.read_bytes() == before
        assert not sandbox.exists() or not list(sandbox.iterdir())


def text(result: ParsedDocument, page: int | None = None) -> str:
    return " ".join(
        b.text
        for b in result.blocks
        if page is None or (b.locator.kind == "pdf" and b.locator.page == page)
    )


def report(result: ParsedDocument) -> None:
    assert result.ocr
    print(
        json.dumps(
            {
                "page_count": result.page_count,
                "quality": result.quality,
                "ocr": result.ocr.model_dump(),
                "excerpt": text(result)[:180],
            },
            ensure_ascii=False,
        )
    )


def scan(path: Path, texts: list[str]) -> None:
    writer = PdfWriter()
    for index, value in enumerate(texts):
        raster = path.parent / f"raster{index}.png"
        image(raster, value)
        page_pdf = path.parent / f"page{index}.pdf"
        with Image.open(raster) as bitmap:
            bitmap.save(page_pdf, "PDF", resolution=216)
        writer.add_page(PdfReader(page_pdf).pages[0])
    writer.set_page_label(0, len(texts) - 1, style="/r")
    writer.write(path)


@pytest.mark.parametrize("suffix,value", [(".png", VI), (".jpg", EN), (".jpeg", VI)])
def test_image_phrases_and_raw_pixel_locator(tmp_path: Path, suffix: str, value: str) -> None:
    path = tmp_path / ("scan" + suffix)
    image(path, value)
    result = parse(path)
    assert value in text(result)
    assert result.quality == "ocr" and result.page_count is None
    assert result.ocr and result.ocr.attempted_pages == (1,)
    for index, block in enumerate(result.blocks):
        assert block.extraction_method == "ocr"
        locator = block.locator
        assert locator.kind == "image" and locator.image_id == identity(path).sha256
        assert locator.ocr_block == index and locator.bbox
        box = locator.bbox
        assert 0 <= box.x0 < box.x1 <= 1800 and 0 <= box.y0 < box.y1 <= 420
        # Original source crop contains actual nonwhite text, not an invented box.
        with Image.open(path) as original:
            assert (
                original.crop((box.x0, box.y0, box.x1, box.y1)).convert("L").getextrema()[0] < 100
            )
    report(result)


def test_scan_pdf_en_vi_physical_pages_offsets_and_boxes(tmp_path: Path) -> None:
    path = tmp_path / "scan.pdf"
    scan(path, [EN, VI])
    result = parse(path)
    assert result.page_count == 2 and result.ocr and result.ocr.completed_pages == (1, 2)
    assert EN in text(result, 1) and VI in text(result, 2)
    for page_number in (1, 2):
        page_blocks = [b for b in result.blocks if b.locator.page == page_number]
        canonical = "\n".join(b.text for b in page_blocks)
        for block in page_blocks:
            locator = block.locator
            assert locator.kind == "pdf" and locator.offsets
            assert locator.printed_page_label == ("i" if page_number == 1 else "ii")
            assert canonical[locator.offsets.start : locator.offsets.end] == block.text
            assert block.bbox and 0 <= block.bbox[0] < block.bbox[2] <= 600
    report(result)


def test_image_exif_dpi_preserve_raw_pixel_provenance(tmp_path: Path) -> None:
    path = tmp_path / "camera.jpg"
    image(path, VI)
    with Image.open(path) as original:
        tagged = original.copy()
    exif = Image.Exif()
    exif[274] = 6  # Display rotated 90 degrees; source pixels are still landscape.
    tagged.save(path, exif=exif, dpi=(600, 600), quality=95)
    tagged.close()
    result = parse(path)
    assert VI in text(result)
    for block in result.blocks:
        locator = block.locator
        assert locator.kind == "image" and locator.bbox
        box = locator.bbox
        assert 0 <= box.x0 < box.x1 <= 1800 and 0 <= box.y0 < box.y1 <= 420
        with Image.open(path) as original:
            assert (
                original.crop((box.x0, box.y0, box.x1, box.y1)).convert("L").getextrema()[0] < 100
            )
    print("PASS EXIF orientation6/DPI600: phrase + bboxes retain original raw source pixels")


def test_mixed_and_existing_text_layer_not_duplicated(tmp_path: Path) -> None:
    native = tmp_path / "native.pdf"
    pdf(native, [[EN]])
    raster = tmp_path / "raster.pdf"
    scan(raster, [VI])
    path = tmp_path / "mixed.pdf"
    writer = PdfWriter()
    writer.add_page(PdfReader(native).pages[0])
    writer.add_page(PdfReader(raster).pages[0])
    writer.add_page(PdfReader(native).pages[0])
    writer.write(path)
    result = parse(path)
    assert result.ocr and result.ocr.attempted_pages == (2,) and result.ocr.completed_pages == (2,)
    assert text(result).count(EN) == 2 and text(result).count(VI) == 1
    assert all(b.extraction_method == "native" for b in result.blocks if b.locator.page in (1, 3))
    assert VI in text(result, 2)
    # OCR enabled with a missing data directory is still unnecessary for native-only PDF.
    native_result = parse(native, ocr=OcrConfig(enabled=True, tessdata_path=tmp_path / "absent"))
    assert native_result.quality == "text" and native_result.ocr is None
    report(result)


def test_searchable_scan_layer_not_ocr_again(tmp_path: Path) -> None:
    path = tmp_path / "layer.png"
    image(path, VI)
    subprocess.run(
        ["tesseract", str(path), str(tmp_path / "searchable"), "-l", "vie+eng", "pdf"],
        check=True,
        capture_output=True,
        timeout=20,
    )
    result = parse(tmp_path / "searchable.pdf")
    assert VI in text(result) and text(result).count(VI) == 1
    assert result.ocr is None and result.quality == "text"
    print("PASS actual searchable scan image + Tesseract text layer: no OCR retry, phrase once")


@pytest.mark.parametrize("suffix", [".png", ".pdf"])
def test_status_blank_and_unreadable(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / ("blank" + suffix)
    if suffix == ".pdf":
        scan(path, [""])
    else:
        image(path, "")
    with pytest.raises(ParseError, match=r"^ocr_empty$"):
        parse(path)
    print(f"PASS {suffix} blank/unreadable -> ocr_empty; source unchanged; sandbox empty")


def test_status_partial_pdf_cannot_hide_blank_page(tmp_path: Path) -> None:
    path = tmp_path / "partial.pdf"
    scan(path, [VI, ""])
    result = parse(path)
    assert result.quality == "partial" and result.needs_ocr_pages == (2,)
    assert result.ocr and result.ocr.completed_pages == (1,)
    assert result.warnings == ("ocr_unreadable_pages",)
    report(result)


def test_status_missing_tessdata(tmp_path: Path) -> None:
    path = tmp_path / "scan.png"
    image(path)
    empty = tmp_path / "tessdata"
    empty.mkdir()
    with pytest.raises(ParseError, match=r"^ocr_tessdata_missing$"):
        parse(path, ocr=OcrConfig(enabled=True, tessdata_path=empty))
    print("PASS real Tesseract with empty tessdata -> ocr_tessdata_missing; cleanup")


def test_status_missing_vie_and_corrupt_tessdata(tmp_path: Path) -> None:
    path = tmp_path / "scan.png"
    image(path)
    data = tmp_path / "data"
    data.mkdir()
    shutil.copyfile("/usr/share/tesseract-ocr/5/tessdata/eng.traineddata", data / "eng.traineddata")
    with pytest.raises(ParseError, match=r"^ocr_tessdata_missing$"):
        parse(path, ocr=OcrConfig(enabled=True, tessdata_path=data))
    (data / "vie.traineddata").write_bytes(b"corrupt data")
    (data / "eng.traineddata").write_bytes(b"corrupt data")
    with pytest.raises(ParseError, match=r"^ocr_failed$"):
        parse(path, ocr=OcrConfig(enabled=True, tessdata_path=data))
    print("PASS missing vie -> ocr_tessdata_missing; corrupt eng/vie -> technical ocr_failed")


def test_status_missing_engine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "scan.png"
    image(path)
    monkeypatch.setenv("PATH", str(tmp_path / "no-binary"))
    with pytest.raises(ParseError, match=r"^ocr_engine_missing$"):
        parse(path)
    print("PASS actual unavailable CLI -> ocr_engine_missing")


def test_status_output_limit(tmp_path: Path) -> None:
    path = tmp_path / "scan.png"
    image(path)
    with pytest.raises(ParseError, match=r"^extraction_limit$"):
        parse(path, limits=ParserLimits(max_blocks=1))


def test_status_corrupt_image_and_mime(tmp_path: Path) -> None:
    path = tmp_path / "broken.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\ncorrupt")
    with pytest.raises(ParseError, match=r"^corrupt_document$"):
        parse(path)
    image(path)
    mislabeled = tmp_path / "false.jpg"
    mislabeled.write_bytes(path.read_bytes())
    with pytest.raises(ParseError, match=r"^mime_mismatch$"):
        parse(mislabeled)
    print("PASS corrupt/image signature mismatch explicit errors; cleanup")


@pytest.mark.parametrize("suffix", [".png", ".pdf"])
def test_status_pixel_limits_before_render(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / ("oversize" + suffix)
    if suffix == ".pdf":
        scan(path, [VI])
    else:
        image(path)
    with pytest.raises(ParseError, match=r"^image_limit$"):
        parse(path, limits=ParserLimits(max_image_pixels=1000))
    print(f"PASS {suffix} pixel allocation bounded before render/decode")


def tesseract_pids() -> set[int]:
    pids = set()
    for entry in Path("/proc").iterdir():
        if entry.name.isdecimal():
            try:
                if (entry / "comm").read_text().strip() == "tesseract" and b"stdout" in (
                    entry / "cmdline"
                ).read_bytes():
                    pids.add(int(entry.name))
            except OSError:
                pass
    return pids


@pytest.mark.parametrize("action", ["cancel", "timeout"])
def test_status_cancel_timeout_reaps_real_tesseract(tmp_path: Path, action: str) -> None:
    path = tmp_path / "large.png"
    # Many independent text lines keep the real CLI busy long enough to interrupt.
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    with Image.new("RGB", (2400, 9000), "white") as bitmap:
        drawing = ImageDraw.Draw(bitmap)
        for y in range(40, 8900, 45):
            drawing.text((40, y), VI + " " + EN, font=font, fill="black")
        bitmap.save(path)
    cancel = threading.Event()
    seen: set[int] = set()
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            parse,
            path,
            cancel=cancel,
            limits=ParserLimits(timeout_seconds=8 if action == "timeout" else 30),
        )
        while not future.done() and time.monotonic() - started < 7:
            seen = tesseract_pids()
            if seen:
                break
            time.sleep(0.02)
        assert seen, "Real Tesseract child must start before interruption"
        if action == "cancel":
            cancel.set()
        with pytest.raises(
            ParseError, match=f"^parser_{'cancelled' if action == 'cancel' else 'timeout'}$"
        ):
            future.result(timeout=15)
    # A killed orphan can briefly be a zombie until PID1 reaps it; no running child.
    for pid in seen:
        state = Path(f"/proc/{pid}/stat")
        assert not state.exists() or state.read_text().split()[2] == "Z"
    print(
        f"PASS {action}: observed actual Tesseract children={len(seen)}, killed process group; cleanup; elapsed={time.monotonic() - started:.3f}s"
    )


def test_status_disabled_ocr_explicit(tmp_path: Path) -> None:
    path = tmp_path / "scan.png"
    image(path)
    with pytest.raises(ParseError, match=r"^ocr_required$"):
        parse(path, ocr=OcrConfig(enabled=False))
