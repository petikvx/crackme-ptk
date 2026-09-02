# Solution — xor-bytes-easy-3

## Password

```
FecqT2A5LKYM
```

## How it works

1. The binary stores the password XOR-encoded with key `0x3c`.
2. At runtime it decodes into a temporary buffer and `strcmp`s against the user input.
3. Seed used for generation: `153`.

## Quick check

```bash
./xor-bytes-easy-3 'FecqT2A5LKYM'
```
