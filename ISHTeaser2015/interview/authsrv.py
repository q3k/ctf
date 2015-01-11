import socket
import hashlib
import os

USERS = {
    'foo': 'bar'
}

SOCKET = '/tmp/authserver.sock'

if os.path.exists(SOCKET):
   os.remove(SOCKET) 
s = socket.socket(1, socket.SOCK_STREAM)
s.bind(SOCKET)
s.listen(100)

while True:
    c, _ = s.accept()
    line = c.recv(1024)
    magic, username, nonce, password = line.split(':')
    if magic != 'check_auth':
        print "Invalid request"
        c.send(chr(0))
        c.close()
    else:
        print "Auth request from {}, {}:{}".format(nonce, username, password)
        if username in USERS:
            h = hashlib.sha256(nonce+USERS[username]).hexdigest()
            print "OK"
            c.send(chr(1))
            c.close()
        else:
            print "Invalid username or password."
            c.send(chr(0))
            c.close()

