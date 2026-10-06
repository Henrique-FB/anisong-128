"""Pull the most-playlisted AnimeThemes entries into data/candidates.json.

tracks_count = how many AnimeThemes user playlists include the entry; it's our popularity signal.
"""
import json, time, urllib.request, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "candidates.json"
URL = ("https://api.animethemes.moe/animethemeentry?sort=-tracks_count&page%5Bsize%5D=100&page%5Bnumber%5D={n}"
       "&include=animetheme.anime,animetheme.song.artists,videos")
PAGES = 25

rows = []
for n in range(1, PAGES + 1):
    req = urllib.request.Request(URL.format(n=n), headers={"User-Agent": "Mozilla/5.0 (amq-brackets)"})
    data = json.load(urllib.request.urlopen(req))
    for e in data["animethemeentries"]:
        t, vids = e["animetheme"], e.get("videos") or []
        a, s = t["anime"], t.get("song") or {}
        best = max(vids, key=lambda v: (not v["lyrics"], v["nc"], -v["size"]), default=None)
        rows.append({
            "anime": a["name"], "anime_slug": a["slug"], "year": a["year"], "format": a["media_format"],
            "type": t["type"], "slug": t["slug"] + (f"v{e['version']}" if (e.get("version") or 1) > 1 else ""),
            "song": s.get("title"), "artists": ", ".join(x["name"] for x in s.get("artists") or []),
            "playlists": e["tracks_count"], "spoiler": e["spoiler"], "nsfw": e["nsfw"],
            "video": best and best["basename"], "size_mb": best and round(best["size"] / 1e6, 1),
            "resolution": best and best["resolution"],
        })
    print(n, len(rows), rows[-1]["playlists"])
    time.sleep(0.7)

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
print("wrote", OUT)
