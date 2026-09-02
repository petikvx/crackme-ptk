# Challenges

Each folder `cm-YYYY-NNN/` is one generated challenge.

- `public/` — safe for players
- `private/` — **author only** (sources, SOLUTION.md, secrets in `challenge.yml`)
- `dist/` — local builds (gitignored)

If this Git repository is public, anything under `private/` and the `private:` block of `challenge.yml` is visible. Prefer a **private** repo and publish only Release zips produced by `ptk pack`.
