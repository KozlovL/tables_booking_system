# src/utils/images.py
import base64
import binascii
import os
import uuid

MEDIA_ROOT = "media/cafes"
MEDIA_URL_PREFIX = "/media/cafes"


def save_base64_image(b64: str) -> str:
    if not b64:
        raise ValueError("empty base64")
    if ";base64," in b64:
        b64 = b64.split(";base64,", 1)[1]
    try:
        raw = base64.b64decode(b64, validate=True)
    except binascii.Error as e:
        raise ValueError(f"invalid base64: {e!s}")

    # определим расширение грубой эвристикой
    ext = ".jpg"
    if raw[:8].startswith(b"\x89PNG"): ext = ".png"
    elif raw[:3] == b"\xff\xd8\xff":   ext = ".jpg"
    elif raw[:4] == b"GIF8":           ext = ".gif"

    os.makedirs(MEDIA_ROOT, exist_ok=True)
    fname = f"{uuid.uuid4().hex}{ext}"
    fpath = os.path.join(MEDIA_ROOT, fname)
    with open(fpath, "wb") as f:
        f.write(raw)
    return f"{MEDIA_URL_PREFIX}/{fname}"  # кладём в БД


def file_url_to_base64(url: str | None) -> str | None:
    if not url:
        return None
    rel = url.lstrip("/")
    if not os.path.exists(rel):
        return None
    with open(rel, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")
