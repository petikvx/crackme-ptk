; xor-bytes-easy-asm — FASM crackme (PE32)
; Seed=65  XOR key=0xe4
;
; Build: fasm main.asm xor-bytes-easy-asm.exe

format PE console
entry start

section '.data' data readable writeable
  usage db 'Usage: xor-bytes-easy-asm.exe <password>',13,10,0
  granted db 'Access granted!',13,10,0
  denied db 'Access denied.',13,10,0
  enc db 0xa5,0x97,0x97,0xa3,0xd6,0x8b,0xa7,0xa0,0xac,0xa7,0xae,0xd3,0
  enc_len = $ - enc - 1
  xor_key db 0xe4
  decoded rb 64

section '.code' code readable executable

; ---- skip argv0 on command line (EDI/RDI = ptr) → points at password or 0 ----
skip_argv0:

  mov al, [edi]
  cmp al, '"'
  jne .sp
  inc edi
.q: mov al, [edi]
  test al, al
  jz .done
  inc edi
  cmp al, '"'
  jne .q
  jmp .sp
.sp: mov al, [edi]
  test al, al
  jz .done
  cmp al, ' '
  je .sp2
  cmp al, 9
  je .sp2
  inc edi
  jmp .sp
.sp2: mov al, [edi]
  test al, al
  jz .done
  cmp al, ' '
  je .sk
  cmp al, 9
  je .sk
  jmp .done
.sk: inc edi
  jmp .sp2
.done: ret


; null-terminate password at first space/tab (in-place on cmdline buffer — OK for crackme)
terminate_arg:

  mov esi, edi
.t: mov al, [esi]
  test al, al
  jz .ok
  cmp al, ' '
  je .cut
  cmp al, 9
  je .cut
  inc esi
  jmp .t
.cut: mov byte [esi], 0
.ok: ret


decode_password:

  lea ebx, [enc]
  lea ebp, [decoded]
  xor ecx, ecx
.d: cmp ecx, enc_len
  jae .de
  mov al, [ebx+ecx]
  xor al, [xor_key]
  mov [ebp+ecx], al
  inc ecx
  jmp .d
.de: mov byte [ebp+ecx], 0
  ret


start:

  call [GetCommandLineA]
  mov edi, eax
  call skip_argv0
  mov al, [edi]
  test al, al
  jz .bad_usage
  call terminate_arg
  call decode_password
  push decoded
  push edi
  call [strcmp]
  add esp, 8
  test eax, eax
  jnz .fail
  push granted
  call [printf]
  add esp, 4
  push 0
  call [ExitProcess]
.fail:
  push denied
  call [printf]
  add esp, 4
  push 1
  call [ExitProcess]
.bad_usage:
  push usage
  call [printf]
  add esp, 4
  push 1
  call [ExitProcess]


section '.idata' import data readable writeable
  dd 0,0,0,RVA kernel_name,RVA kernel_table
  dd 0,0,0,RVA msvcrt_name,RVA msvcrt_table
  dd 0,0,0,0,0


kernel_table:
  ExitProcess dd RVA _ExitProcess
  GetCommandLineA dd RVA _GetCommandLineA
  dd 0
msvcrt_table:
  printf dd RVA _printf
  strcmp dd RVA _strcmp
  dd 0


kernel_name db 'KERNEL32.DLL',0
msvcrt_name db 'msvcrt.dll',0

_ExitProcess dw 0
  db 'ExitProcess',0
_GetCommandLineA dw 0
  db 'GetCommandLineA',0
_printf dw 0
  db 'printf',0
_strcmp dw 0
  db 'strcmp',0
