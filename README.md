# crackme-ptk

Generate Linux **crackmes** / **keygenmes**, keep **sources + solutions private**, and publish **player packs** (ELF + README) via **GitHub Actions / Releases / Pages**.

Inspired by [crackmes.one](https://crackmes.one/), but focused on a generator + GitHub-native workflow.

## Layout

```
generator/     CLI (ptk)
templates/     language × type skeletons
challenges/    generated instances (public/ + private/)
catalog/       public index JSON
site/          GitHub Pages catalogue
```

Each challenge:

| Path | Visibility |
|------|------------|
| `public/` | Shipped to players |
| `private/` | Author only (sources, SOLUTION.md, secrets) |
| `dist/` | Local/CI build outputs (gitignored binaries/zips) |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Generate
ptk gen --type crackme --lang c --difficulty 1 --name xor-gate-easy
ptk gen --type keygenme --lang c --difficulty 1 --name serial-mix-easy

# Build + verify + public zip
ptk all challenges/cm-YYYY-001

# Refresh catalogue for the site
ptk catalog
```

### CLI

| Command | Purpose |
|---------|---------|
| `ptk gen` | Create challenge from templates |
| `ptk build` | Compile ELF into `dist/` |
| `ptk verify` | Author checks (known password/serial) |
| `ptk pack` | Zip public files + leak-check |
| `ptk all` | build → verify → pack |
| `ptk catalog` | Write `catalog/index.json` + `site/catalog.json` |

## Public vs private

- **Players** get a zip: stripped ELF + `README.md` (and optional public extras).
- **You** keep `private/src`, `private/SOLUTION.md`, and secrets in `challenge.yml`.
- `ptk pack` refuses archives that embed `private/`, `SOLUTION`, or plaintext secrets in text files.

Recommended: keep this repo **private**, publish packs with Actions Releases, host the catalogue on Pages. Optionally mirror only public artefacts to a separate public repo later.

## GitHub

1. Push the repo to GitHub.
2. Enable **Pages** (GitHub Actions source).
3. Set `window.PTK_RELEASE_BASE` in `site/config.js` to  
   `https://github.com/<user>/<repo>/releases/download`
4. Publish a challenge:

```text
Actions → Build challenge → Run workflow → challenge_id = cm-2026-001
```

That builds, verifies, packs, and creates a Release named after the challenge id.

## Templates (MVP)

- `templates/c/crackme/difficulty-1` — XOR-encoded password
- `templates/c/keygenme/difficulty-1` — seeded username→serial mix

More languages (ASM, Rust, Go, Python) and types (patchme, unpackme) follow the same layout.

## License

MIT for the generator and templates. Challenge binaries you publish remain under terms you choose; keep them educational.
