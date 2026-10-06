# AMQ Brackets — project notes

Living notes for Claude. Read this first; update it as decisions are made.

## Goal
A 128-song anime opening/ending bracket ("anisong" tournament) to play with friends.

## v1 (2026-10-06) — "Anisong 128" Claude artifact
- URL: https://claude.ai/artifact/Kgksn9nVtB1uqSSZt6D8SF (owned by user, shared via link)
- Single HTML page, ~7.4 MB (128 base64 WebP covers embedded). Tabs: Play / Bracket / Gallery.
- Data: MAL top anime, one entry per franchise, one song each; videos from
  `v.animethemes.moe/<Name>-OP1.webm`; "playlists" field = AnimeThemes playlist count.
- Multiplayer: artifact `db` + `user` capabilities. Owner/editor = host who advances winners;
  others vote into `votes/{uid}`. Rules: state read=view write=admin; votes/{self} write=interact.
- Standard seeding (1v128, 64v65...), 127 matches, arrow keys pick left/right.

### What the user disliked (priority order)
1. **Friends joining** — hard to join; some friends have no Claude account and won't make one.
   Requirement: no-account friends must at least **listen and see votes** (voting optional for them).
2. **Listening** — "Listen" opened the webm in a new tab (no side-by-side); songs lagged / slow to load.
3. **Song + anime picks** — mediocre/weird. Sequel/movie entries with obscure songs instead of the
   iconic one (e.g. AoT got *Shoukei to Shikabane no Michi*, Gintama an ED, One Piece "Fan Letter" ED),
   ~20 entries missing artists, inconsistent seeding vs MAL rank.
   User wants Claude to **research and hand-curate 128 good songs/anime** instead of auto-picking.

### What to keep (user didn't complain)
- Bracket / gallery views, covers, seeding concept.

## Research log

### 2026-10-06 — why v1 failed, and what's possible
**Claude artifacts and friends who don't have accounts**
- Public artifact links open with no sign-in on Pro/Max (official docs: code.claude.com/docs/en/artifacts).
- BUT the `db` capability resolves `null` for signed-out viewers (artifact-capabilities skill), so
  people without an account see the static page with **no live votes**. Comments are also hidden from
  public-link-only visitors. `assets` makes the page org-internal (never public).
- CSP: fetch/XHR only reach the page's own origin, and external images are blocked. External <audio>
  is unconfirmed (probably blocked, which would explain v1 using new-tab links). Published `files`
  allow 15 MB per binary file and 64 MB per version, so 128 short opus clips (~350 KB each) would fit.
- Conclusion: artifacts can't do "no-account friends see live votes" without hacks (host republishing
  the page on every pick). Hosting it ourselves is the better fit.

**Why audio lagged**
- v1 linked 720p `.webm` videos, ~30 MB each (Cowboy Bebop OP1 = 30.2 MB).
- AnimeThemes has audio-only files: `https://a.animethemes.moe/<Name>.ogg` (~3.7 MB). They support Range
  requests (206). They're served `Cache-Control: no-cache, private` from a single nginx origin behind
  Cloudflare, i.e. not CDN-cached, so they can still be slow. Fix: preload the next match, or
  self-host short trimmed clips (ffmpeg is installed).
- API: `https://api.animethemes.moe/video/<basename>?include=audio` returns sizes and the audio link.
  GraphQL is at graphql.animethemes.moe. The per-theme "playlists" count = a popularity signal.

**Existing tools (none fit well)**
- AnimeBracket.com (now run by AnimeThemes): community polls, image-based, rounds run over days.
  I believe login is required to vote (not verified).
- BracketFights: fill out a bracket solo and share it. Not live group play.
- Challonge: bracket admin only, no media.
- Discord call + screen-share + reaction votes: zero build, but no bracket view.

**Sources for curating songs**
- r/anime Best Opening contests (winners: FMAB "again", Steins;Gate "Hacking to the Gate",
  Tokyo Ghoul "unravel", Cowboy Bebop "Tank!"...).
- Spotify most-streamed anime songs (Gurenge, Kaikai Kitan, unravel, Inferno, Silhouette...).
- Crunchyroll Anime Awards Best Opening/Song; MAL "Top 25 OPs" article.
- AnimeThemes playlist counts, aggregated per franchise across all its themes (v1 only looked at one season).

### Local tooling available
ffmpeg, node, python 3.12, gh (logged in as Henrique-FB), git (Git Bash).

## Decisions (2026-10-06)
- Played **live on a call**: the user streams their screen and runs the voting. Voting doesn't need
  to be synchronous or happen in-app.
- **Visuals matter**: play the actual OP/ED videos, not audio only.
- OPs and EDs both allowed. **One song per franchise.** No friends' AniList/MAL lists.
- **Rejected: GitHub Pages + database.** Too much setup for what the user wants.
- **Agreed shape: two pages.**
  1. **Friends' page:** every entry numbered, with search and a play button. No account needed.
  2. **Host page (streamed):** bracket and matches showing the same numbers, so friends can type
     "#42" into search. Plan: a **local HTML file** on the user's PC playing **pre-downloaded videos**.
     No CSP limits and no streaming lag. The 128 videos are ~6.1 GB.
- **Update 2026-10-06: no Claude artifacts at all.** The user wants inline video on the friends' page,
  and the artifact CSP blocks external media. The friends' page therefore moved to **GitHub Pages**,
  as one static file with no backend.

## Project layout
- `scripts/fetch_candidates.py` pulls the top 2,500 AnimeThemes entries by playlist count into `data/candidates.json`.
- `data/picks.txt` holds the hand-curated 128 (`anime | slug | optional song title` when names are ambiguous).
- `scripts/build_songs.py` turns picks.txt into `data/songs.json` and assigns seeds by playlist count.
  `data/songs.md` is the readable table.
- The anime name and video basename come from the AnimeThemes data. Several entries have no artist listed there.

## v2 build (2026-10-06): user approved the draft 128 as-is
They know most songs, so playback is occasional. Not every match gets played.
- Templates: `pages/base.css` (shared tokens/cards, v1 look: Dela Gothic One + IBM Plex, magenta/teal),
  `pages/friends.html`, `pages/host.html`. Placeholders: `/*__CSS__*/ /*__SONGS__*/ /*__COVERS__*/`.
- `python scripts/build_pages.py` writes `dist/site/index.html` (friends) and `dist/host.html` (~2.4 MB each, covers inlined).
- **Friends' page: https://henrique-fb.github.io/anisong-128/** (public repo github.com/Henrique-FB/anisong-128).
  `.github/workflows/pages.yml` runs build_pages.py and deploys `dist/site` on every push to main,
  so **to update it, commit and push**. `dist/` is gitignored.
  The page has a numbered grid, search (a number matches exactly), OP/ED filters, and a Play button
  that opens a modal `<video>` streaming from `v.animethemes.moe`. If a video errors, the modal links
  to `https://animethemes.moe/anime/<anime_slug>/<slug>`.
- The old artifact (https://claude.ai/artifact/Kgksn9nVtB1uqSSZt6D8SF) is no longer used.
- **Host page:** open `dist/host.html` locally. Tabs: Match / Bracket / All songs. Keys 1 and 2 pick
  the left/right winner (arrow keys deliberately unbound so seeking a video can't pick a winner).
  Videos play from `dist/videos/<basename>` and fall back to `v.animethemes.moe` on error.
  State is saved in localStorage (`anisong128-host-v2`), with Save backup / Load backup JSON buttons.
- `scripts/download_videos.py` is resumable (.part files) and logs to dist/download.log.
  AnimeThemes returned 503 after ~27 back-to-back downloads, so the script pauses 5 s between
  files and retries with backoff (30 s → 5 min).
- The local host page has no artifact shell, so base.css carries its own `[hidden]{display:none!important}`.
  Without it, the modal backdrop covered the whole page.
- Fixing a song: edit `data/picks.txt`, then run build_songs.py → fetch_covers.py → build_pages.py,
  commit + push (redeploys the friends' page), and re-run download_videos.py.
  Seeds change when picks change, so don't edit picks mid-bracket.
