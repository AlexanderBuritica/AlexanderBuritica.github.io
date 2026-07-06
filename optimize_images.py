"""
optimize_images.py
------------------------------------------------------------
Comprime y redimensiona las imágenes pesadas del sitio para
mejorar el rendimiento (Core Web Vitals) y el SEO.

- Crea una copia de respaldo de cada archivo original en
  files/images/_backup_originals/ antes de modificarlo.
- Redimensiona la foto principal a 600x680 aprox (calidad 82).
- Redimensiona el favicon a 64x64.
- Redimensiona todas las fotos de fieldwork a un máximo de
  1200 px de ancho (calidad 82).

Uso:
    pip install Pillow
    python optimize_images.py
------------------------------------------------------------
"""

import os
import shutil
from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "files", "images")
FIELD_DIR = os.path.join(IMG_DIR, "fieldwork")
BACKUP_DIR = os.path.join(IMG_DIR, "_backup_originals")

os.makedirs(BACKUP_DIR, exist_ok=True)


def backup(path):
    """Guarda una copia del original una sola vez."""
    rel = os.path.relpath(path, IMG_DIR)
    dest = os.path.join(BACKUP_DIR, rel.replace(os.sep, "__"))
    if not os.path.exists(dest):
        shutil.copy2(path, dest)


def kb(path):
    return os.path.getsize(path) / 1024


def optimize(path, max_w=None, max_h=None, quality=82, to_size=None):
    if not os.path.exists(path):
        print(f"  [skip] no existe: {path}")
        return
    before = kb(path)
    backup(path)
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)          # respeta orientación EXIF
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if to_size:                                 # favicon: tamaño exacto
        img = img.resize(to_size, Image.LANCZOS)
    else:
        w, h = img.size
        scale = 1.0
        if max_w and w > max_w:
            scale = min(scale, max_w / w)
        if max_h and h > max_h:
            scale = min(scale, max_h / h)
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # guarda como JPG optimizado (mismo nombre/extension)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".jpg", ".jpeg"):
        img.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    elif ext == ".png":
        img.save(path, "PNG", optimize=True)
    after = kb(path)
    print(f"  {os.path.basename(path):32s} {before:8.0f} KB -> {after:7.0f} KB")


def main():
    print("Backups en:", BACKUP_DIR)
    print("\n1) Foto principal:")
    optimize(os.path.join(IMG_DIR, "Alex_Buritaca.JPG"), max_w=600, max_h=680, quality=82)

    print("\n2) Favicon:")
    optimize(os.path.join(IMG_DIR, "icon.PNG"), to_size=(64, 64))

    print("\n3) Fotos de fieldwork (máx 1200 px de ancho):")
    if os.path.isdir(FIELD_DIR):
        for f in sorted(os.listdir(FIELD_DIR)):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                optimize(os.path.join(FIELD_DIR, f), max_w=1200, quality=82)

    print("\n✓ Listo. Originales respaldados en files/images/_backup_originals/")
    print("  Revisa el sitio; si algo se ve mal, restaura desde el backup.")


if __name__ == "__main__":
    main()
