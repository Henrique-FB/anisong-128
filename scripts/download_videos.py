"""Download every bracket video into dist/videos/ so the host page plays from disk (~6 GB). Resumable.

The host page falls back to streaming any file that isn't here, so this is optional.
"""
import json, pathlib, shutil, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "videos"
OUT.mkdir(parents=True, exist_ok=True)
PAUSE = 5                    # seconds between files; AnimeThemes returns 503 when hammered
BACKOFF = [30, 60, 120, 300]


def fetch(name, dest):
    part = dest.with_suffix(".part")
    req = urllib.request.Request("https://v.animethemes.moe/" + name, headers={"User-Agent": "Mozilla/5.0 (amq-brackets)"})
    with urllib.request.urlopen(req, timeout=60) as r, open(part, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    part.rename(dest)


failed = []
for s in json.loads((ROOT / "data" / "songs.json").read_text(encoding="utf-8")):
    dest = OUT / s["video"]
    if dest.exists():
        continue
    for wait in BACKOFF + [None]:
        try:
            fetch(s["video"], dest)
            print(f"{s['n']:>3} {s['video']} {dest.stat().st_size / 1e6:.0f} MB", flush=True)
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if wait is None:
                failed.append(s["n"])
                print(f"{s['n']:>3} FAILED {s['video']}: {e}", flush=True)
            else:
                print(f"{s['n']:>3} {e}; retrying in {wait}s", flush=True)
                time.sleep(wait)
    time.sleep(PAUSE)
print("done;", f"failed: {failed}" if failed else "all downloaded")
