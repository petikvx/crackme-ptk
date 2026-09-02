# Solution — xor-bytes-easy-2

## Password

```
A7PLf43J4PND
```

## How it works

1. The binary stores the password XOR-encoded with key `0x08`.
2. At runtime it decodes into a temporary buffer and `strcmp`s against the user input.
3. Seed used for generation: `57005`.

## Quick check

```bash
./xor-bytes-easy-2 'A7PLf43J4PND'
```
