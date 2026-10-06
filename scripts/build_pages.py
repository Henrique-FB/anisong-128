"""Inject songs, covers and shared CSS into pages/*.html.

dist/site/index.html  friends' page, deployed to GitHub Pages by .github/workflows/pages.yml
dist/host.html        host page, opened locally next to dist/videos/
"""
import base64, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES, DIST = ROOT / "pages", ROOT / "dist"
KEEP = ["n", "anime", "anime_slug", "type", "slug", "song", "artists", "year", "video"]

songs = [{k: s[k] for k in KEEP} for s in json.loads((ROOT / "data" / "songs.json").read_text(encoding="utf-8"))]
covers = {}
for s in songs:
    f = ROOT / "data" / "covers" / f"{s['anime_slug']}.webp"
    if f.exists():
        covers[s["anime_slug"]] = "data:image/webp;base64," + base64.b64encode(f.read_bytes()).decode()

css = (PAGES / "base.css").read_text(encoding="utf-8")
OUTPUTS = {"friends.html": DIST / "site" / "index.html", "host.html": DIST / "host.html"}
for name, out in OUTPUTS.items():
    html = (PAGES / name).read_text(encoding="utf-8")
    html = (html.replace("/*__CSS__*/", css)
                .replace("/*__SONGS__*/", json.dumps(songs, ensure_ascii=False))
                .replace("/*__COVERS__*/", json.dumps(covers)))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(out.relative_to(ROOT), round(len(html.encode()) / 1e6, 2), "MB")
