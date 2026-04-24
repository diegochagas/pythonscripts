#!/usr/bin/env python3
"""Convert image folders to .cbr files (ZIP archives renamed to .cbr).

Images are converted to JPEG and resized if height exceeds MAX_HEIGHT.
Requires: pip install Pillow
"""

import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif"}
MAX_HEIGHT = 2500
JPEG_QUALITY = 90


def get_images(folder: Path) -> list[Path]:
    return sorted(
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )


def process_image(path: Path) -> tuple[bytes, str]:
    """Return (jpeg_bytes, filename) for the image, resized if needed."""
    with Image.open(path) as img:
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        if img.height > MAX_HEIGHT:
            ratio = MAX_HEIGHT / img.height
            new_size = (int(img.width * ratio), MAX_HEIGHT)
            img = img.resize(new_size, Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)

    return buf.getvalue(), path.stem + ".jpg"


def make_cbr(image_folder: Path, output_dir: Path) -> Path:
    images = get_images(image_folder)
    if not images:
        return None

    zip_path = output_dir / f"{image_folder.name}.zip"
    cbr_path = output_dir / f"{image_folder.name}.cbr"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        for img_path in images:
            data, filename = process_image(img_path)
            zf.writestr(filename, data)
            print(f"    + {filename}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        zipped_count = len(zf.namelist())

    if zipped_count != len(images):
        zip_path.unlink()
        print(f"  ERROR: '{image_folder.name}' — expected {len(images)} images, zip has {zipped_count}. Aborted.")
        return None

    zip_path.rename(cbr_path)
    print(f"  Created: {cbr_path} ({len(images)} images)")
    return cbr_path


def process(root: Path):
    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.")
        sys.exit(1)

    subfolders = [f for f in root.iterdir() if f.is_dir()]
    root_images = get_images(root)

    if subfolders:
        print(f"Found {len(subfolders)} subfolder(s) in '{root.name}' — processing each:")
        for subfolder in sorted(subfolders):
            make_cbr(subfolder, root)
    elif root_images:
        print(f"Found {len(root_images)} image(s) in '{root.name}' — creating CBR:")
        make_cbr(root, root.parent)
    else:
        print("No images or subfolders with images found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_cbr.py <folder>")
        sys.exit(1)

    process(Path(sys.argv[1]))
