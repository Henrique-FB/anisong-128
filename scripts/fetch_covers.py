"""Download a small WebP cover per song into data/covers/<anime_slug>.webp (skips ones already present)."""
import json, pathlib, subprocess, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "covers"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (amq-brackets)"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()


for s in json.loads((ROOT / "data" / "songs.json").read_text(encoding="utf-8")):
    dest = OUT / f"{s['anime_slug']}.webp"
    if dest.exists():
        continue
    imgs = json.loads(get(f"https://api.animethemes.moe/anime/{s['anime_slug']}?include=images"))["anime"]["images"]
    img = next((i for i in imgs if i["facet"] == "Large Cover"), None) or (imgs[0] if imgs else None)
    if not img:
        print("NO COVER", s["anime"])
        continue
    raw = OUT / "tmp_src"
    raw.write_bytes(get(img["link"]))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw), "-vf", "scale=220:-2",
                    "-quality", "72", str(dest)], check=True)
    raw.unlink()
    print(s["n"], dest.name, dest.stat().st_size // 1024, "KB")
    time.sleep(0.4)
