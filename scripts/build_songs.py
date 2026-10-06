"""Resolve data/picks.txt against data/candidates.json -> data/songs.json (seeded by playlist count)."""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
cands = json.loads((ROOT / "data" / "candidates.json").read_text(encoding="utf-8"))

picks, errors = [], []
for line in (ROOT / "data" / "picks.txt").read_text(encoding="utf-8").splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    name, slug, *song = [p.strip() for p in line.split("|")]
    pool = [c for c in cands if c["slug"] == slug and (not song or c["song"] == song[0])]
    hits = [c for c in pool if c["anime"] == name] or [c for c in pool if c["anime"].startswith(name)]
    if len(hits) != 1:
        errors.append(f"{name} | {slug}: {len(hits)} matches {[h['anime'] for h in hits][:4]}")
        continue
    picks.append(hits[0])

for e in errors:
    print("UNRESOLVED", e)
if len(picks) != 128:
    print(f"have {len(picks)} picks, need 128")

picks.sort(key=lambda c: -c["playlists"])
songs = [{"n": i + 1, **c} for i, c in enumerate(picks)]
(ROOT / "data" / "songs.json").write_text(json.dumps(songs, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", len(songs), "songs")
sys.exit(1 if errors else 0)
