# PDF to CBR Converter

Converts a folder of PDF files into CBR (Comic Book Reader) format. Each PDF page is rendered as a JPG image, then all images are packaged into a ZIP archive and renamed to `.cbr`.

## How it works

For each PDF found in the target folder:

1. Renders every page as a JPG image at the specified DPI
2. Verifies the extracted image count matches the PDF page count
3. Compresses all JPGs into a ZIP archive named after the PDF
4. Renames the ZIP to `.cbr`

CBR files can be opened with any comic book reader such as [CDisplayEx](https://www.cdisplayex.com/), [Calibre](https://calibre-ebook.com/), or similar apps.

## Requirements

- Python 3.7+
- [PyMuPDF](https://pymupdf.readthedocs.io/)

Install the dependency with:

```
pip install pymupdf
```

## Usage

### Basic usage

Pass the path to the folder containing your PDFs:

```
python pdf_to_cbr.py "C:\path\to\your\pdfs"
```

### Interactive mode (no argument)

If you omit the folder path, the script will prompt you to enter it:

```
python pdf_to_cbr.py
```

### Options

| Flag             | Description                                | Default              |
| ---------------- | ------------------------------------------ | -------------------- |
| `--dpi <number>` | Rendering resolution in DPI                | `150`                |
| `--overwrite`    | Re-convert PDFs that already have a `.cbr` | Off (skips existing) |

### Examples

Convert PDFs at the default 150 DPI:

```
python pdf_to_cbr.py "C:\path\to\your\pdfs"
```

Convert at higher quality (300 DPI):

```
python pdf_to_cbr.py "C:\path\to\your\pdfs" --dpi 300
```

Re-convert all PDFs, even if a `.cbr` already exists:

```
python pdf_to_cbr.py "C:\path\to\your\pdfs" --overwrite
```

Combine both options:

```
python pdf_to_cbr.py "C:\path\to\your\pdfs" --dpi 200 --overwrite
```

## Output

The `.cbr` files are saved in the same folder as the source PDFs. Each file is named after its source PDF (e.g. `my-comic.pdf` → `my-comic.cbr`).

## Notes

- Files that already have a corresponding `.cbr` are skipped by default. Use `--overwrite` to force re-conversion.
- Duplicate PDFs with the same base name (e.g. `file.pdf` and `file.pdf.pdf`) are deduplicated automatically — only the cleanest name is processed.
- A summary is printed at the end showing how many files were converted, skipped, warned, or errored.
