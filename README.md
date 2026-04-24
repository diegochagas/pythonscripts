# Python Scripts

A collection of utility scripts for working with images and comic book archives.

---

## pdf_to_cbr.py

Converts a folder of PDF files into CBR (Comic Book Reader) format. Each PDF page is rendered as a JPG image, then all images are packaged into a ZIP archive and renamed to `.cbr`.

### How it works

For each PDF found in the target folder:

1. Renders every page as a JPG image at the specified DPI
2. Verifies the extracted image count matches the PDF page count
3. Compresses all JPGs into a ZIP archive named after the PDF
4. Renames the ZIP to `.cbr`

### Requirements

- Python 3.7+
- [PyMuPDF](https://pymupdf.readthedocs.io/)

```
pip install pymupdf
```

### Usage

```
python pdf_to_cbr.py <folder> [--dpi <number>] [--overwrite]
```

If you omit the folder path, the script will prompt you to enter it.

| Flag             | Description                                | Default              |
| ---------------- | ------------------------------------------ | -------------------- |
| `--dpi <number>` | Rendering resolution in DPI                | `150`                |
| `--overwrite`    | Re-convert PDFs that already have a `.cbr` | Off (skips existing) |

### Examples

```
python pdf_to_cbr.py "C:\path\to\pdfs"
python pdf_to_cbr.py "C:\path\to\pdfs" --dpi 300
python pdf_to_cbr.py "C:\path\to\pdfs" --dpi 200 --overwrite
```

### Output

`.cbr` files are saved in the same folder as the source PDFs, named after each source PDF (e.g. `my-comic.pdf` → `my-comic.cbr`). Files that already have a `.cbr` are skipped by default; use `--overwrite` to force re-conversion.

---

## make_cbr.py

Packages a folder of images directly into a `.cbr` file (a ZIP archive renamed to `.cbr`) without any PDF conversion step. Useful when you already have image files and just want to bundle them into a comic book archive.

### How it works

- If the target folder contains **subfolders**, each subfolder is packaged into its own `.cbr` file and saved alongside the subfolders in the parent directory.
- If the target folder contains **images directly** (no subfolders), the entire folder is packaged into a single `.cbr` saved in the parent directory.

Supported image formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.tiff`, `.tif`

### Requirements

- Python 3.7+ (standard library only — no extra dependencies)

### Usage

```
python make_cbr.py <folder>
```

### Examples

Pack each subfolder of a directory into its own CBR:

```
python make_cbr.py "C:\path\to\comics"
```

Pack all images in a single folder into one CBR:

```
python make_cbr.py "C:\path\to\chapter1"
```

---

## images_to_cbr.py

Packages a folder of images into a `.cbr` file (a ZIP archive renamed to `.cbr`) without any image conversion or resizing. Images are added exactly as they are. Useful when you want to bundle existing images as-is, preserving their original format and quality.

### How it works

- If the target folder contains **subfolders**, each subfolder is packaged into its own `.cbr` file saved alongside the subfolders in the parent directory.
- If the target folder contains **images directly** (no subfolders), the entire folder is packaged into a single `.cbr` saved in the parent directory.

Before renaming the ZIP to `.cbr`, the script verifies that every expected image file is present in the archive by name. If any are missing, the ZIP is deleted and an error is reported.

Supported image formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.tiff`, `.tif`

### Requirements

- Python 3.10+ (standard library only — no extra dependencies)

### Usage

```
python images_to_cbr.py <folder>
```

### Examples

Pack each subfolder of a directory into its own CBR:

```
python images_to_cbr.py "C:\path\to\comics"
```

Pack all images in a single folder into one CBR:

```
python images_to_cbr.py "C:\path\to\chapter1"
```

### Difference from make_cbr.py

| Feature | `make_cbr.py` | `images_to_cbr.py` |
| --- | --- | --- |
| Image conversion | Converts to JPEG | None — files copied as-is |
| Resizing | Yes (max height 2500 px) | No |
| Dependencies | Pillow | None |

---

## rotate_images.py

Rotates all images in a folder by a specified number of degrees, overwriting the originals in place.

### Requirements

- Python 3.7+
- [Pillow](https://pillow.readthedocs.io/)

```
pip install pillow
```

### Usage

```
python rotate_images.py <folder> [degrees]
```

`degrees` defaults to `90` if not specified.

### Examples

Rotate all images 90 degrees clockwise:

```
python rotate_images.py "C:\path\to\images"
```

Rotate all images 180 degrees:

```
python rotate_images.py "C:\path\to\images" 180
```

### Notes

- Images are overwritten in place — make a backup first if needed.
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.tiff`, `.webp`

---

CBR files can be opened with any comic book reader such as [CDisplayEx](https://www.cdisplayex.com/), [Calibre](https://calibre-ebook.com/), or similar apps.
