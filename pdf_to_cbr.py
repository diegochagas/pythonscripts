#!/usr/bin/env python3
"""
PDF to CBR Converter
====================
For each PDF in a folder:
  1. Renders every page as a JPG image (equivalent to Acrobat's "Export All Images")
  2. Verifies the extracted image count matches the PDF page count
  3. Compresses all JPGs into a ZIP archive named after the PDF
  4. Renames the ZIP to CBR

Usage:
  python pdf_to_cbr.py                           # prompts for folder path
  python pdf_to_cbr.py C:\\path\\to\\folder         # pass folder as argument
  python pdf_to_cbr.py C:\\path\\to\\folder --dpi 200   # custom DPI (default: 150)
  python pdf_to_cbr.py C:\\path\\to\\folder --overwrite # reconvert existing CBRs

Requirements:
  pip install pymupdf
  (No other external dependencies needed — works on Windows, macOS, Linux)
"""

import sys
import zipfile
import tempfile
import argparse
from pathlib import Path


def check_dependencies():
    try:
        import fitz  # noqa: F401  (PyMuPDF)
    except ImportError:
        print("ERROR: PyMuPDF is not installed.")
        print("       Run:  pip install pymupdf")
        sys.exit(1)


def clean_stem(path: Path) -> str:
    """Return base filename with ALL .pdf extensions stripped (handles .pdf.pdf)."""
    stem = path.name
    while True:
        p = Path(stem)
        if p.suffix.lower() == ".pdf":
            stem = p.stem
        else:
            stem = stem.rstrip(".")
            break
    return stem


def pdf_to_cbr(pdf_path: Path, dpi: int = 150, skip_existing: bool = True) -> dict:
    """
    Convert one PDF to a CBR file.
    Renders each page as JPEG using PyMuPDF (no poppler needed).
    Returns a dict: name, pages, images, cbr_path, status, error
    """
    import fitz  # PyMuPDF

    result = dict(name=pdf_path.name, pages=0, images=0,
                  cbr_path=None, status="ok", error=None)

    stem = clean_stem(pdf_path)
    output_dir = pdf_path.parent
    cbr_path = output_dir / f"{stem}.cbr"

    if skip_existing and cbr_path.exists():
        print(f"  [SKIP] {cbr_path.name} already exists")
        result.update(status="skipped", cbr_path=cbr_path)
        return result

    try:
        doc = fitz.open(str(pdf_path))
        page_count = len(doc)
        result["pages"] = page_count
        print(f"  Pages : {page_count}")
        print(f"  Extracting pages as JPG (DPI={dpi})...")

        # PyMuPDF uses a zoom matrix; 72 dpi is the base, so zoom = dpi / 72
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            jpg_paths = []

            for page_num in range(page_count):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                jpg_name = f"{stem}_{page_num + 1:04d}.jpg"
                jpg_file = tmp / jpg_name
                pix.save(str(jpg_file))   # PyMuPDF saves as JPEG when ext is .jpg
                jpg_paths.append(jpg_file)
                del pix  # free memory immediately

            doc.close()

            extracted = len(jpg_paths)
            result["images"] = extracted

            if extracted != page_count:
                print(f"  WARNING: {page_count} pages but {extracted} images!")
                result["status"] = "warning"
            else:
                print(f"  Images : {extracted} ✓  (matches page count)")

            # Build ZIP (no compression — CBR readers expect raw JPGs)
            zip_path = output_dir / f"{stem}.zip"
            with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_STORED) as zf:
                for jpg_file in sorted(jpg_paths):
                    zf.write(str(jpg_file), jpg_file.name)

        # Rename ZIP → CBR
        if cbr_path.exists():
            cbr_path.unlink()
        zip_path.rename(cbr_path)
        result["cbr_path"] = cbr_path
        print(f"  Saved : {cbr_path.name}")

    except Exception as exc:
        result.update(status="error", error=str(exc))
        print(f"  ERROR: {exc}")

    return result


def process_folder(folder_path: str, dpi: int = 150, skip_existing: bool = True):
    folder = Path(folder_path).expanduser().resolve()

    if not folder.exists():
        print(f"ERROR: Folder not found: {folder}")
        sys.exit(1)

    # Collect PDFs (case-insensitive suffix)
    pdf_files = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() == ".pdf"
    )

    # Deduplicate by clean stem — keeps the file with the shorter (cleaner) name
    seen: dict = {}
    for p in pdf_files:
        stem = clean_stem(p)
        if stem not in seen or len(p.name) < len(seen[stem].name):
            seen[stem] = p
    pdf_files = sorted(seen.values(), key=lambda x: x.name)

    if not pdf_files:
        print(f"No PDF files found in: {folder}")
        return

    total = len(pdf_files)
    print(f"Found {total} PDF file(s) in: {folder}")
    print(f"DPI: {dpi}  |  Skip existing CBRs: {skip_existing}")
    print("=" * 60)

    results = []
    for idx, pdf in enumerate(pdf_files, start=1):
        print(f"\n[{idx}/{total}] {pdf.name}")
        sys.stdout.flush()
        r = pdf_to_cbr(pdf, dpi=dpi, skip_existing=skip_existing)
        results.append(r)

    ok      = sum(1 for r in results if r["status"] == "ok")
    warned  = sum(1 for r in results if r["status"] == "warning")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors  = sum(1 for r in results if r["status"] == "error")

    print("\n" + "=" * 60)
    print(f"DONE — {ok} converted | {warned} warnings | {skipped} skipped | {errors} errors")

    if errors:
        print("\nFailed files:")
        for r in results:
            if r["status"] == "error":
                print(f"  - {r['name']}: {r['error']}")

    if warned:
        print("\nPage-count mismatches:")
        for r in results:
            if r["status"] == "warning":
                print(f"  - {r['name']}: {r['pages']} pages vs {r['images']} images")


def main():
    check_dependencies()

    parser = argparse.ArgumentParser(
        description="Convert PDF files to CBR (Comic Book Reader) format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("folder", nargs="?", default=None,
                        help="Path to folder containing PDFs (prompted if omitted)")
    parser.add_argument("--dpi", type=int, default=150,
                        help="Rendering resolution in DPI (default: 150)")
    parser.add_argument("--overwrite", action="store_true", default=False,
                        help="Re-convert even if a .cbr already exists")
    args = parser.parse_args()

    folder = args.folder
    if not folder:
        folder = input("Enter the path to the folder containing PDF files: ").strip()
        if not folder:
            print("No path provided. Exiting.")
            sys.exit(1)

    process_folder(folder, dpi=args.dpi, skip_existing=not args.overwrite)


if __name__ == "__main__":
    main()
