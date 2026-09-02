# challenge.yml schema

```yaml
id: cm-2026-001
name: xor-gate-easy
type: crackme          # crackme | keygenme | patchme | unpackme
language: c            # c | cpp | asm | rust | go | python
arch: windows-x86_64   # or linux-x86_64 (~88% windows by default at gen time)
difficulty: 1          # 1..5
summary: "..."
tags: [crackme, c, diff-1]
created: "2026-03-22"

public:
  readme: public/README.md
  binary_name: xor-gate-easy

private:
  source_dir: private/src
  solution: private/SOLUTION.md
  flag_or_key: "..."
  password: "..."          # crackme
  example_user: alice      # keygenme
  example_serial: "...."

params:
  seed: 123456
  algo: xor_bytes
  xor_key: 42
```

**Rule:** anything under `private` must never enter the public zip or Pages download assets.
