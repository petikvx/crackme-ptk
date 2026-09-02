# xor-bytes-easy-asm

**Type:** crackme  
**Language:** asm (FASM)  
**Difficulty:** 1  
**OS:** windows  
**PE format:** PE32  
**Arch:** windows-x86

Password-protected PE32 binary. The secret is XOR-encoded.

## Goal

Find the correct password so the program prints `Access granted!`.

## Run

```bat
xor-bytes-easy-asm.exe <password>
```

## Rules

- Target: Windows PE32 (32-bit)
- Assembled with **FASM**
- Author sources and solutions are **not** included in this pack
