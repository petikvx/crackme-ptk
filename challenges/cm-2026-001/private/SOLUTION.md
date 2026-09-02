# Solution — xor-gate-easy

## Password

```
9LNlbhQBmtX8
```

## How it works

1. The binary stores the password XOR-encoded with key `0x4b`.
2. At runtime it decodes into a temporary buffer and `strcmp`s against the user input.
3. Seed used for generation: `12648430`.

## Quick check

```bash
./xor-gate-easy '9LNlbhQBmtX8'
```
