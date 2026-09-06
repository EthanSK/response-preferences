#!/usr/bin/env python3
"""Keep one original user message and its supplied images behind a reply link."""
import hashlib
import json
from pathlib import Path
import shutil
import sys


def create_context(source, destination):
    data = json.loads(Path(source).read_text(encoding="utf-8"))
    if not isinstance(data.get("text"), str):
        raise ValueError("text must contain the original user message")
    images = data.get("images", [])
    if not isinstance(images, list) or not all(isinstance(p, str) for p in images):
        raise ValueError("images must be a list of supplied image paths")
    destination = Path(destination).resolve()
    if destination.suffix != ".md":
        raise ValueError("output must be a new .md file")
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    parts = ["# Your message\n", data["text"], ""]
    if images:
        parts.append("## Attached images\n")
    for index, value in enumerate(images, 1):
        image = Path(value).expanduser()
        if not image.is_file():
            parts.append(f"Image {index}: original attachment is no longer available.\n")
            continue
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        folder = destination.parent / "attachments"
        folder.mkdir(exist_ok=True)
        copied = folder / (digest + image.suffix.lower())
        if not copied.exists():
            shutil.copy2(image, copied)
        # Angle brackets protect Markdown image targets containing spaces.
        parts.append(f"![Attached image {index}](<{copied}>)\n")
    with destination.open("x", encoding="utf-8") as output:
        output.write("\n".join(parts))
    return destination


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: create-reply-context.py input.json new-context.md")
    print(create_context(sys.argv[1], sys.argv[2]))
