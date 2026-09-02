# Solution — serial-mix-easy

## Algorithm

Seed constant in binary: `0x12345678`

1. `state = seed ^ 0x9E3779B9`
2. For each username byte `c`:
   - `state = state * 1664525 + c + 1013904223` (mod 2³²)
   - `state ^= state << 13`
   - `state ^= state >> 17`
   - `state ^= state << 5`
3. Four times: `state = state * 1664525 + 1013904223`, append `state & 0xFFFF` as 4 hex digits, joined by `-`.

## Example

- User: `alice`
- Serial: `FB94-B1E3-6DE6-2C0D`

```bash
./serial-mix-easy alice FB94-B1E3-6DE6-2C0D
```

## Sample table

- `alice` → `FB94-B1E3-6DE6-2C0D`
- `bob` → `144A-7721-260C-A9FB`
- `petik` → `512A-CE81-D5EC-D85B`
- `root` → `67F9-7104-4893-34D6`
- `guest` → `97AF-6142-2FB9-15C4`

