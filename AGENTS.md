# AGENTS.md — crackme-ptk

Instructions for coding agents working in this repo.

## Product in one line

Generate educational crackmes/keygenmes, keep **sources + solutions private**, publish **player packs** (binary + README) via GitHub Actions / Releases / Pages.

## WIP privé → promote (important)

Sometimes the user studies a **specific** crackme/keygenme with the agent first, then wants it added to the catalogue later.

### Triggers

| User intent | What to do |
|-------------|------------|
| **WIP / à part / on étudie / ne publie pas** | Design + implement locally only. **Do not** commit, push, run Release workflow, or put the challenge in the public catalogue flow unless asked. |
| **Promouvoir / ajouter au catalogue / release** | Turn the WIP into a real `challenges/cm-YYYY-NNN/`, run `ptk all`, update catalogue, commit/push, and/or guide Release — only what the user asks. |

### Default WIP behaviour

1. Build the challenge with the user (algo, arch, lang, difficulty, name).
2. Prefer writing under `challenges/_wip/<slug>/` (or paths the user gives). Keep `private/` (source + `SOLUTION.md`) and a short `notes.md` if useful.
3. **Do not** create a GitHub Release or assume publication.
4. When the user later says to promote it: assign next `cm-YYYY-NNN`, finalize `challenge.yml`, `ptk all`, `ptk catalog`, then commit/push/release as requested.

The user will often ask for steps 2–3 **directly** in chat (“fais le WIP”, “promouvois …”). Treat those as explicit mode switches — no need to re-explain the workflow unless asked.

## Tooling

- CLI: `ptk` (`gen`, `build`, `verify`, `pack`, `all`, `catalog`) — see `README.md`, `docs/fasm.md`, `docs/challenge-schema.md`.
- Default arch mix when `--arch` omitted: ~88% Windows, among Windows ~50/50 `windows-x86` (PE32) / `windows-x86_64` (PE32+); rest Linux.
- `language: asm` → **FASM**, Windows PE only for now.
- Never ship `private/` or solutions in public zips (`ptk pack` leak-checks).

## Safety

- Educational reverse-engineering only.
- Prefer keeping the GitHub repo **private** while it contains solutions under `challenges/*/private/`.
