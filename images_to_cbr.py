#!/usr/bin/env python3
"""Pack image folders into .cbr files (ZIP archives renamed to .cbr).

Images are added as-is — no conversion or resizing.
"""

import sys
import zipfile
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif"}


def get_images(folder: Path) -> list[Path]:
    return sorted(
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )


def pack_cbr(image_folder: Path, output_dir: Path) -> Path | None:
    images = get_images(image_folder)
    if not images:
        print(f"  SKIP: '{image_folder.name}' — no images found.")
        return None

    zip_path = output_dir / f"{image_folder.name}.zip"
    cbr_path = output_dir / f"{image_folder.name}.cbr"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        for img_path in images:
            zf.write(img_path, img_path.name)
            print(f"    + {img_path.name}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        zipped_names = set(zf.namelist())

    expected_names = {img.name for img in images}
    missing = expected_names - zipped_names
    if missing:
        zip_path.unlink()
        print(
            f"  ERROR: '{image_folder.name}' — {len(missing)} file(s) missing from zip "
            f"({', '.join(sorted(missing))}). Aborted."
        )
        return None

    zip_path.rename(cbr_path)
    print(f"  Created: {cbr_path} ({len(images)} images)")
    return cbr_path


def process(root: Path) -> None:
    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.")
        sys.exit(1)

    subfolders = sorted(f for f in root.iterdir() if f.is_dir())
    root_images = get_images(root)

    if subfolders:
        print(f"Found {len(subfolders)} subfolder(s) in '{root.name}' — processing each:")
        for subfolder in subfolders:
            pack_cbr(subfolder, root)
    elif root_images:
        print(f"Found {len(root_images)} image(s) in '{root.name}' — creating CBR:")
        pack_cbr(root, root.parent)
    else:
        print("No images or subfolders with images found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python images_to_cbr.py <folder>")
        sys.exit(1)

    process(Path(sys.argv[1]))
