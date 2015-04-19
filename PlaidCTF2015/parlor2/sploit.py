import pwn

from Crypto.PublicKey import RSA, DSA
from Crypto.Random import random, atfork
from Crypto.Cipher import PKCS1_OAEP

_server_pub_enc = RSA.importKey('-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDGRrsdIqf8K39Ncwzsi9k2lr5G\nJ8aEFkYGrYqOQRbU5xOReMj8wWHgnSUC0fjH0gjffGiUC2HfrrNIQvXKGiSBetOu\nIWOmFiESG8IhrPyvLwX53NbMWeCihzbYGJxGyiL0bvDHxqDxzuvteSaEfNm1miPA\nQ9rs5vFnHM0R3kFjdQIDAQAB\n-----END PUBLIC KEY-----')

server_pub_enc = PKCS1_OAEP.new(_server_pub_enc)

dsakey = DSA.generate(512)

parts = ','.join([str(p) for p in [dsakey.y, dsakey.g, dsakey.p, dsakey.q]])
parts_encrypted = []
for i in range(len(parts)/40+1):
    part = parts[i*40:(i+1)*40]
    print part
    part_encrypted = server_pub_enc.encrypt(part).encode('hex')
    parts_encrypted.append(part_encrypted)

r = pwn.remote("52.6.11.111", 4321)
r.send(','.join(parts_encrypted))
print r.recvuntil("communications\n")
print r.recvuntil('\n')

# Only winning move is to play
print r.recvuntil('game?\n')
print r.recvuntil('\n')
r.send(str(100000000000000000000000000) + '\n')
print r.recvuntil('\n')
print r.recvuntil('\n')
r.send(str(2) + '\n')
print r.recvuntil('\n')

privkey = RSA.generate(1024)
privkey_exported = privkey.exportKey()
privkey_oaep = PKCS1_OAEP.new(privkey)

guess = "I hereby commit to a guess of 0"
guess_encrypted = privkey_oaep.encrypt(guess).encode('hex')
guess_signature = ','.join([str(l) for l in dsakey.sign(guess_encrypted, random.randint(1, dsakey.q))])

r.send(guess_encrypted+'~'+guess_signature)
print r.recvuntil('\n')
print r.recvuntil('\n')
print r.recvuntil('\n')
privkey_signature = ','.join([str(l) for l in dsakey.sign(privkey_exported, random.randint(1, dsakey.q))])
r.send(privkey_exported+'~'+privkey_signature)
print r.recvuntil('\n')
print r.recvuntil('\n')
print r.recvuntil('\n')

