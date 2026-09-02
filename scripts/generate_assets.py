"""Generate Android icon and presplash images for Gudo Snake."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def draw_snake_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (18, 28, 18, 255))
    draw = ImageDraw.Draw(img)

    margin = size // 8
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=size // 10,
        fill=(34, 120, 58, 255),
        outline=(180, 230, 180, 255),
        width=max(2, size // 64),
    )

    cell = size // 10
    snake = [
        (3, 5), (4, 5), (5, 5), (6, 5), (6, 4), (6, 3), (5, 3), (4, 3), (3, 3), (3, 4),
    ]
    colors = [(255, 220, 80), (120, 210, 90), (90, 180, 70), (70, 150, 55)]
    origin_x = size // 2 - cell * 3
    origin_y = size // 2 - cell * 2

    for index, (gx, gy) in enumerate(snake):
        x = origin_x + gx * cell
        y = origin_y + gy * cell
        color = colors[index % len(colors)]
        draw.rounded_rectangle(
            (x, y, x + cell - 2, y + cell - 2),
            radius=cell // 4,
            fill=color,
        )

    eye = cell // 5
    draw.ellipse(
        (origin_x + 6 * cell - eye * 2, origin_y + 3 * cell, origin_x + 6 * cell, origin_y + 3 * cell + eye * 2),
        fill=(20, 20, 20, 255),
    )

    food_x = origin_x + 2 * cell
    food_y = origin_y + 6 * cell
    draw.ellipse((food_x, food_y, food_x + cell, food_y + cell), fill=(220, 60, 60, 255))
    return img


def draw_presplash() -> Image.Image:
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), (12, 18, 12))
    draw = ImageDraw.Draw(img)

    icon = draw_snake_icon(512)
    img.paste(icon, ((width - 512) // 2, (height - 512) // 2 - 120), icon)

    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except OSError:
        font = ImageFont.load_default()

    title = "Gudo Snake"
    bbox = draw.textbbox((0, 0), title, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((width - text_w) // 2, (height + 512) // 2 - 40), title, fill=(220, 235, 220), font=font)
    return img


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)

    icon = draw_snake_icon(512)
    icon.save(ASSETS / "icon.png")

    adaptive = draw_snake_icon(432)
    adaptive.save(ASSETS / "icon_foreground.png")

    bg = Image.new("RGBA", (432, 432), (18, 28, 18, 255))
    bg.save(ASSETS / "icon_background.png")

    presplash = draw_presplash()
    presplash.save(ASSETS / "presplash.png")

    print(f"Generated assets in {ASSETS}")


if __name__ == "__main__":
    main()
