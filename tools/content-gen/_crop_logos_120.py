import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
from pathlib import Path

base = next(Path(r"g:\O meu disco\AUTOMAÇÕES\assets\projetos").glob("120. NEG*PORTO*"))
print("base:", base)
banners = base / "identidade-visual" / "banners"
for f in banners.iterdir():
    print(" -", repr(f.name))

src = next(f for f in banners.iterdir() if f.suffix.lower() == ".png" and "FORMS" in f.name.upper())
print("src:", src.name)
dst = base / "LOGOS"
dst.mkdir(exist_ok=True)

im = Image.open(src)
W, H = im.size
po = im.crop((int(W*0.665), int(H*0.30), int(W*0.78), int(H*0.66)))
po.save(dst / "porto_itapoa_logo.png")
print("ok porto", po.size)
