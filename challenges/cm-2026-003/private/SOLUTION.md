# Solution — xor-bytes-easy

## Password

```
2VMcZyBNjdda
```

## How it works

1. The binary stores the password XOR-encoded with key `0x75`.
2. At runtime it decodes into a temporary buffer and `strcmp`s against the user input.
3. Seed used for generation: `126786512`.

## Quick check

```bash
./xor-bytes-easy '2VMcZyBNjdda'
```
