"""Generates the website's static assets from the HeartPath app repo.

Usage: python make_site_assets.py <app repo> <website dir>
"""
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

app = Path(sys.argv[1])
site = Path(sys.argv[2])
fonts_in = app / "assets/fonts"
img = site / "assets/img"
fonts_out = site / "assets/fonts"
img.mkdir(parents=True, exist_ok=True)
fonts_out.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- icons
F, B = "Fill", "Bold"
ICONS = {
    "heart": (0xE2A8, F), "heartbeat": (0xE2AC, F), "walk": (0xE73A, F),
    "pill": (0xE700, F), "symptoms": (0xE198, F), "mood": (0xE6CC, F),
    "book": (0xE8F2, F), "chart": (0xE150, F), "report": (0xE23A, F),
    "siren": (0xE9B8, F), "lock": (0xE2FA, F), "offline": (0xE4F2, F),
    "phone": (0xE1E0, F), "shield": (0xE40C, F), "download": (0xE20C, B),
    "check": (0xE182, B), "check-circle": (0xE184, F), "android": (0xE008, F),
    "apple": (0xE516, F), "qr": (0xE3E6, F), "folder": (0xE24A, F),
    "tap": (0xEC90, F), "gear": (0xE270, F), "arrow-down": (0xE03E, B),
    "users": (0xE4D6, F), "envelope": (0xE214, F), "clock": (0xE19A, F),
    "refresh": (0xE036, B), "trash": (0xE4A6, F), "translate": (0xE4A2, F),
    "question": (0xE3E8, F), "seal-check": (0xE606, F), "x-circle": (0xE4F8, F),
    "caret-down": (0xE136, B), "toggle": (0xE676, F), "bell": (0xE5E8, F),
    "warning": (0xE4E0, F), "info": (0xE2CE, F), "sparkle": (0xE6A2, F),
    "arrow-right": (0xE06C, B), "x": (0xE4F6, B), "file-down": (0xE232, F),
    "backup": (0xE1AE, F), "call": (0xE3BA, F), "breath": (0xE5D2, F),
    "calendar": (0xE10A, F), "chevron-right": (0xE13A, B), "wifi-off": (0xE4F2, F),
}
fonts = {s: TTFont(fonts_in / f"Phosphor-{s}.ttf") for s in (F, B)}
symbols = []
for name, (cp, style) in ICONS.items():
    font = fonts[style]
    glyph_name = font.getBestCmap()[cp]
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs)
    gs[glyph_name].draw(pen)
    # Font units are y-up with the baseline at 960 of a 1024 em.
    symbols.append(
        f'<symbol id="i-{name}" viewBox="0 0 1024 1024">'
        f'<path transform="matrix(1 0 0 -1 0 960)" d="{pen.getCommands()}"/></symbol>'
    )
sprite = (
    '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">'
    + "".join(symbols)
    + "</svg>"
)
(img / "icons.svg").write_text(sprite)

# ---------------------------------------------------------------- fonts
LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2190-2193,U+2212,U+2215"


def woff2(src, dst, unicodes=None):
    f = TTFont(fonts_in / src)
    if unicodes:
        opts = Options()
        opts.layout_features = ["*"]
        sub = Subsetter(opts)
        ranges = []
        for part in unicodes.split(","):
            part = part.replace("U+", "")
            if "-" in part:
                a, b = part.split("-")
                ranges.extend(range(int(a, 16), int(b, 16) + 1))
            else:
                ranges.append(int(part, 16))
        sub.populate(unicodes=ranges)
        sub.subset(f)
    f.flavor = "woff2"
    f.save(fonts_out / dst)


woff2("PlusJakartaSans-ExtraBold.ttf", "jakarta-800.woff2", LATIN)
woff2("AtkinsonHyperlegibleNext-Regular.ttf", "atkinson-400.woff2", LATIN)
woff2("AtkinsonHyperlegibleNext-Bold.ttf", "atkinson-700.woff2", LATIN)
woff2("NotoSansSinhala-Regular.ttf", "sinhala-400.woff2")
woff2("NotoSansSinhala-Bold.ttf", "sinhala-700.woff2")
woff2("NotoSansTamil-Regular.ttf", "tamil-400.woff2")
woff2("NotoSansTamil-Bold.ttf", "tamil-700.woff2")

# ---------------------------------------------------------------- images
icon = Image.open(app / "assets/branding/app_icon.png").convert("RGBA")
icon_square = Image.open(app / "assets/branding/app_icon_ios.png").convert("RGB")
icon.resize((256, 256), Image.LANCZOS).save(img / "app-icon.png", optimize=True)
icon.resize((96, 96), Image.LANCZOS).save(img / "app-icon-96.png", optimize=True)
icon_square.resize((180, 180), Image.LANCZOS).save(img / "apple-touch-icon.png", optimize=True)
icon_square.resize((512, 512), Image.LANCZOS).save(img / "icon-512.png", optimize=True)
icon_square.resize((192, 192), Image.LANCZOS).save(img / "icon-192.png", optimize=True)
icon.resize((48, 48), Image.LANCZOS).save(img / "favicon.png", optimize=True)

shots = img / "screens"
shots.mkdir(exist_ok=True)
for name in [
    "home_en", "home_si", "exercise", "exercise_session", "charts_bp",
    "medications", "symptoms", "mood", "lesson", "reports",
]:
    s = Image.open(app / f"test_screenshots/goldens/{name}.png").convert("RGB")
    s.save(shots / f"{name}.webp", "WEBP", quality=82, method=6)

# Link preview for WhatsApp / Facebook (1200 x 630).
W, H = 1200, 630
og = Image.new("RGB", (W, H))
px = og.load()
top, bottom = (20, 148, 139), (8, 74, 71)
for y in range(H):
    for x in range(W):
        t = (x / W * 0.6 + y / H * 0.4)
        px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
og = og.convert("RGBA")
glow = Image.new("RGBA", og.size, (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse((760, -300, 1400, 340), fill=(255, 255, 255, 24))
og.alpha_composite(glow)
d = ImageDraw.Draw(og)
logo = icon_square.resize((150, 150), Image.LANCZOS)
mask = Image.new("L", logo.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, 150, 150), 36, fill=255)
og.paste(logo, (80, 90), mask)
jak = str(fonts_in / "PlusJakartaSans-ExtraBold.ttf")
d.text((80, 270), "HeartPath", font=ImageFont.truetype(jak, 92), fill="white")
d.text((84, 385), "Home cardiac rehabilitation app", font=ImageFont.truetype(
    str(fonts_in / "AtkinsonHyperlegibleNext-Bold.ttf"), 40), fill=(225, 245, 242))
x = 84
for text, path, size in [
    ("සිංහල", "NotoSansSinhala-Bold.ttf", 40),
    ("  ·  ", "AtkinsonHyperlegibleNext-Bold.ttf", 40),
    ("தமிழ்", "NotoSansTamil-Bold.ttf", 36),
    ("  ·  ", "AtkinsonHyperlegibleNext-Bold.ttf", 40),
    ("English", "AtkinsonHyperlegibleNext-Bold.ttf", 40),
]:
    f = ImageFont.truetype(str(fonts_in / path), size)
    d.text((x, 455), text, font=f, fill="white")
    x += d.textlength(text, font=f)
# Free · Android pill
pill_font = ImageFont.truetype(str(fonts_in / "AtkinsonHyperlegibleNext-Bold.ttf"), 30)
label = "Free  ·  Android"
w = d.textlength(label, font=pill_font)
pill = Image.new("RGBA", og.size, (0, 0, 0, 0))
ImageDraw.Draw(pill).rounded_rectangle((84, 530, 84 + w + 48, 582), 26, fill=(255, 255, 255, 46))
og.alpha_composite(pill)
d = ImageDraw.Draw(og)
d.text((108, 538), label, font=pill_font, fill="white")
phone = Image.open(app / "test_screenshots/goldens/home_en.png").convert("RGB")
phone = phone.resize((330, round(phone.height * 330 / phone.width)), Image.LANCZOS).crop((0, 0, 330, 560))
pm = Image.new("L", phone.size, 0)
ImageDraw.Draw(pm).rounded_rectangle((0, 0, 330, 600), 40, fill=255)
shadow = Image.new("RGBA", (330 + 120, 560 + 120), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle((60, 60, 390, 660), 40, fill=(0, 0, 0, 110))
shadow = shadow.filter(ImageFilter.GaussianBlur(24))
og.alpha_composite(shadow, (790 - 60, 70 - 50))
og.paste(phone, (790, 70), pm)
og.convert("RGB").save(img / "og-image.jpg", quality=88, optimize=True)

print("assets written")
