# FASM (assembleur)

Les challenges `language: asm` sont compilés avec **Flat Assembler**.

## Installation

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install fasm
fasm
# → flat assembler  version …
```

### Téléchargement officiel

```bash
# Linux (binaire)
curl -LO https://flatassembler.net/fasm-1.73.35.tgz
tar xzf fasm-1.73.35.tgz
chmod +x fasm/fasm.x64
export PATH="$PWD/fasm:$PATH"
fasm.x64
```

Ce dépôt embarque aussi `third_party/fasm/fasm.x64` (utilisé si `fasm` n’est pas dans le `PATH`).

### Windows (optionnel, pour les INCLUDE win32a/win64a)

Nos templates asm sont **autonomes** (pas besoin de `INCLUDE`).
Si tu écris tes propres sources avec `include 'win32a.inc'` :

```bat
:: télécharger fasmw*.zip depuis https://flatassembler.net/download.php
set INCLUDE=C:\fasmw\INCLUDE
fasm main.asm out.exe
```

## Syntaxe de build (ptk)

```bash
# PE32 (32-bit)
ptk gen --type crackme --lang asm --difficulty 1 --arch windows-x86
ptk all challenges/cm-YYYY-NNN

# PE32+ (64-bit)
ptk gen --type crackme --lang asm --difficulty 1 --arch windows-x86_64
ptk all challenges/cm-YYYY-NNN
```

Équivalent manuel :

```bash
fasm challenges/cm-YYYY-NNN/private/src/main.asm challenges/cm-YYYY-NNN/dist/name.exe
```

## Distinctions

| Arch | Format PE | FASM `format` | Bits |
|------|-----------|---------------|------|
| `windows-x86` | **PE32** | `PE console` | 32 |
| `windows-x86_64` | **PE32+** | `PE64 console` | 64 |
