; xor-bytes-easy-asm-2 — FASM crackme (PE32+)
; Seed=66  XOR key=0xe7
;
; Build: fasm main.asm xor-bytes-easy-asm-2.exe

format PE64 console
entry start

section '.data' data readable writeable
  usage db 'Usage: xor-bytes-easy-asm-2.exe <password>',13,10,0
  granted db 'Access granted!',13,10,0
  denied db 'Access denied.',13,10,0
  enc db 0x82,0x93,0xa5,0xd0,0x97,0xbe,0xa4,0x94,0x96,0xd4,0xbe,0xad,0
  enc_len = $ - enc - 1
  xor_key db 0xe7
  decoded rb 64

section '.code' code readable executable

; ---- skip argv0 on command line (EDI/RDI = ptr) → points at password or 0 ----
skip_argv0:

  mov al, [rdi]
  cmp al, '"'
  jne .sp
  inc rdi
.q: mov al, [rdi]
  test al, al
  jz .done
  inc rdi
  cmp al, '"'
  jne .q
  jmp .sp
.sp: mov al, [rdi]
  test al, al
  jz .done
  cmp al, ' '
  je .sp2
  cmp al, 9
  je .sp2
  inc rdi
  jmp .sp
.sp2: mov al, [rdi]
  test al, al
  jz .done
  cmp al, ' '
  je .sk
  cmp al, 9
  je .sk
  jmp .done
.sk: inc rdi
  jmp .sp2
.done: ret


; null-terminate password at first space/tab (in-place on cmdline buffer — OK for crackme)
terminate_arg:

  mov rsi, rdi
.t: mov al, [rsi]
  test al, al
  jz .ok
  cmp al, ' '
  je .cut
  cmp al, 9
  je .cut
  inc rsi
  jmp .t
.cut: mov byte [rsi], 0
.ok: ret


decode_password:

  lea rbx, [enc]
  lea rbp, [decoded]
  xor rcx, rcx
.d: cmp rcx, enc_len
  jae .de
  mov al, [rbx+rcx]
  xor al, [xor_key]
  mov [rbp+rcx], al
  inc rcx
  jmp .d
.de: mov byte [rbp+rcx], 0
  ret


start:

  sub rsp, 28h
  call [GetCommandLineA]
  mov rdi, rax
  call skip_argv0
  mov al, [rdi]
  test al, al
  jz .bad_usage
  call terminate_arg
  call decode_password
  mov rcx, rdi
  lea rdx, [decoded]
  call [strcmp]
  test eax, eax
  jnz .fail
  lea rcx, [granted]
  call [printf]
  xor ecx, ecx
  call [ExitProcess]
.fail:
  lea rcx, [denied]
  call [printf]
  mov ecx, 1
  call [ExitProcess]
.bad_usage:
  lea rcx, [usage]
  call [printf]
  mov ecx, 1
  call [ExitProcess]


section '.idata' import data readable writeable
  dd 0,0,0,RVA kernel_name,RVA kernel_table
  dd 0,0,0,RVA msvcrt_name,RVA msvcrt_table
  dd 0,0,0,0,0


kernel_table:
  ExitProcess dq RVA _ExitProcess
  GetCommandLineA dq RVA _GetCommandLineA
  dq 0
msvcrt_table:
  printf dq RVA _printf
  strcmp dq RVA _strcmp
  dq 0


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
