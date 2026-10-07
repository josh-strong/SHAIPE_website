#!/usr/bin/env python3
"""Create display images without changing the original photographs or figures.

Run from any directory after installing Pillow: python3 scripts/optimise_images.py
The deployed website uses these generated assets directly; no build is needed.
"""

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "img"
OUTPUT = SOURCE / "optimised"

# Each tuple is (source file, output stem, display widths, lossless).
# Figure copies use lossless WebP to preserve labels and plotted values.
IMAGES = [
    ("new_background_pic.png", "background", (960, 1672), False),
    ("logo.png", "logo", (80, 320, 640), True),
    ("IMG_1242.jpg", "team", (720, 1440), False),
    ("fig1 (1).png", "raven-figure", (640, 1979), True),
    ("figure_rq1_flow_web.png", "haic-figure", (800, 1200, 2400), True),
    ("alison-noble-current.jpg", "alison-noble", (320, 640), False),
    ("nick-yeung-current.jpg", "nick-yeung", (320, 640), False),
    ("HH_MScTeach1.jpg", "helen-higham", (320, 640), False),
    ("joshua-strong.jpg", "joshua-strong", (320, 640), False),
    ("emma_sun_picture_Emma Sun.jpg", "emma-sun", (320, 640), False),
    ("IMG_6646_Cheng Ouyang.jpg", "cheng-ouyang", (320, 640), False),
    ("51514f4a-e8ba-4d82-aca8-b2f5632a4513_Harry Rogers.jpeg", "harry-rogers", (320, 640), False),
    ("IMG_4627_Nicholas Phillips.jpg", "nicholas-phillips", (320, 640), False),
    ("IMG_1544_Sajan Patel.jpg", "sajan-patel", (320, 640), False),
    ("Portrait.jpg", "rubeta-matin", (320, 640), False),
    ("processed-65C2E4C2-27B8-4102-B594-A2F262B4B595.jpeg", "ben-attwood", (320, 640), False),
    ("my_photo_James Thomas.jpg", "james-thomas", (320, 640), False),
    ("2a13efb5fc1865393d65f624b70e5dfe.webp", "hilary-edgcombe", (320, 640), False),
    ("bio-picture-sally-shiels.png", "sally-shiels", (320, 640), False),
    ("nathan_g.jpg", "nathan-gauge", (320, 640), False),
    ("Charles Vincent_Charles Vincent.JPG", "charles-vincent", (320, 640), False),
    ("headshot_Anna Todsen.jpg", "anna-todsen", (320, 640), False),
    ("pramit_pic.jpg", "pramit-saha", (320, 640), False),
    ("Bio pic_Rosemary Warren.jpg", "rosie-warren", (320, 640), False),
]


def generate():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for source, stem, widths, lossless in IMAGES:
        with Image.open(SOURCE / source) as original:
            image = ImageOps.exif_transpose(original)
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            for width in sorted({min(width, image.width) for width in widths}):
                height = round(image.height * width / image.width)
                display = image.resize((width, height), Image.Resampling.LANCZOS)
                target = OUTPUT / f"{stem}-{width}.webp"
                display.save(target, "WEBP", lossless=lossless, quality=85, method=6)
                print(f"{target.relative_to(ROOT)}: {width} × {height}, {target.stat().st_size:,} bytes")

    with Image.open(SOURCE / "logo.png") as logo:
        favicon = Image.new("RGBA", (32, 32))
        logo.thumbnail((32, 32), Image.Resampling.LANCZOS)
        favicon.alpha_composite(logo, ((32 - logo.width) // 2, (32 - logo.height) // 2))
        favicon.save(OUTPUT / "favicon-32.png", optimize=True)


if __name__ == "__main__":
    generate()
