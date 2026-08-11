from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps
from tqdm import tqdm

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except:
    pass

# ===========================
# CONFIG
# ===========================

source_input = input("Enter source directory path: ").strip()
if not source_input:
    print("No path found.")
    exit()
else:
    SOURCE = Path(source_input)

if  not SOURCE.exists() : 
    print("Path not found")
    exit()
source_input = source_input.removesuffix("\\")
OUTPUT = Path(source_input+"/webp")

QUALITY = 82
METHOD = 6            # 0-6 (6 = slowest, smallest)
LOSSLESS = False
THREADS = 8

SUPPORTED = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".avif",
    ".heic",
    ".heif"
}

# ===========================

files = [
    f for f in SOURCE.rglob("*")
    if f.suffix.lower() in SUPPORTED
]


def convert(path: Path):

    relative = path.relative_to(SOURCE)

    output = OUTPUT / relative.with_suffix(".webp")

    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists():
        return ("Skipped", path)

    try:

        img = Image.open(path)

        # Auto rotate using EXIF
        img = ImageOps.exif_transpose(img)

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

        img.save(
            output,
            "WEBP",
            quality=QUALITY,
            method=METHOD,
            lossless=LOSSLESS,
            optimize=True,
            exact=False,
        )

        return ("OK", path)

    except Exception as e:
        return ("FAIL", f"{path} : {e}")


ok = 0
skip = 0
fail = 0

with ThreadPoolExecutor(max_workers=THREADS) as pool:

    for result, info in tqdm(pool.map(convert, files), total=len(files)):

        if result == "OK":
            ok += 1
        elif result == "Skipped":
            skip += 1
        else:
            fail += 1
            print(info)

print("\n----------------------")
print("Finished")
print("----------------------")
print("Converted :", ok)
print("Skipped   :", skip)
print("Failed    :", fail)