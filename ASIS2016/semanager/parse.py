import struct
import string
import sys

instructions = {}

def ins(opcode):
    def decorate(f):
        instructions[opcode] = f
        return f
    return decorate

R = [
        'r0',
        'r1',
        'r2',
        'r3',
        'r4',
        'r5',
        'r6',
        'r7',
        'pc',
        'sp',
        'bp',
        'flags',
        'r13'
]

def mode(extra, m):
    if m == 0:
        return 1, R[ord(extra[0])]
    elif m == 1:
        return 1, '[dword ptr {}]'.format(R[ord(extra[0])])
    elif m == 2:
        addr, = struct.unpack('<I', extra[:4])
        return 4, '[dword ptr 0x{:x}]'.format(addr)
    elif m == 4:
        addr, = struct.unpack('<I', extra[:4])
        return 4, '0x{:x}'.format(addr)
    else:
        return 0, '?????'

@ins(0)
def i_mov(pc, i, flags, extra):
    #print hex(ord(flags)), extra.encode('hex')
    used, dst = mode(extra, ord(flags)>>4)
    extra = extra[used:]
    used, src = mode(extra, ord(flags)&0xF)
    return 'mov {}, {}'.format(dst, src)

@ins(1)
def i_sub(pc, i, flags, extra):
    used, dst = mode(extra, ord(flags)>>4)
    extra = extra[used:]
    used, src = mode(extra, ord(flags)&0xF)
    return 'add {}, {}'.format(dst, src)

@ins(2)
def i_sub(pc, i, flags, extra):
    used, dst = mode(extra, ord(flags)>>4)
    extra = extra[used:]
    used, src = mode(extra, ord(flags)&0xF)
    return 'sub {}, {}'.format(dst, src)

@ins(3)
def i_ret(pc, i, flags, extra):
    addr, = struct.unpack('<i', extra[:4])
    if ord(flags):
        return 'call loc_{:x}'.format(addr+pc)
    else:
        return 'call '.format(R[ord(extra[0])])

@ins(4)
def i_cmp(pc, i, flags, extra):
    if ord(flags) != 0:
        left = R[ord(extra[0])]
        right = '0x{:x}'.format(ord(extra[1]))
    else:
        left = R[ord(extra[0])]
        right = R[ord(extra[1])]
    return 'cmp {},{}'.format(left, right)

@ins(5)
def i_jmp(pc, i, flags, extra):
    if ord(flags) != 0:
        addr, = struct.unpack('<i', extra[:4])
        return 'jmp loc_{:x}'.format(addr)
    else:
        return 'jmp {}'.format(R[ord(extra[0])])

@ins(6)
def i_jeq(pc, i, flags, extra):
    if ord(flags) != 0:
        addr, = struct.unpack('<i', extra[:4])
        return 'jeq loc_{:x}'.format(addr+pc)
    else:
        return 'jeq {}'.format(R[ord(extra[0])])

@ins(7)
def i_jne(pc, i, flags, extra):
    if ord(flags) != 0:
        addr, = struct.unpack('<i', extra[:4])
        return 'jne loc_{:x}'.format(addr+pc)
    else:
        return 'jne {}'.format(R[ord(extra[0])])

@ins(10)
def i_push(pc, i, flags, extra):
    if ord(flags):
        addr, = struct.unpack('<I', extra[:4])
        return 'push 0x{:x}'.format(addr)
    else:
        return 'push {}'.format(R[ord(extra[0])])

@ins(11)
def i_pop(pc, i, flags, extra):
    return 'pop {}'.format(R[ord(extra[0])])

@ins(12)
def i_xor(pc, i, flags, extra):
    used, dst = mode(extra, ord(flags)>>4)
    extra = extra[used:]
    used, src = mode(extra, ord(flags)&0xF)
    return 'xor {}, {}'.format(dst, src)


@ins(13)
def i_syscall(pc, i, flags, extra):
    return 'syscall'

@ins(14)
def i_ret(pc, i, flags, extra):
    return 'ret'

with open("target") as b:
    magic, = struct.unpack('<I', b.read(4))
    body_size, = struct.unpack('<I', b.read(4))
    body = b.read(body_size)
    header = body[:2*8]
    header = struct.unpack('<IIII', header)

    page1_offset = header[0]-8
    page2_offset = header[1]-8
    page1_size = header[2]
    page2_size = header[3]

    text = body[page1_offset:page1_offset+page1_size]
    pc = 0

    while pc < page1_size:
        ins = ord(text[pc])
        size = ord(text[pc+2])
        if ins in instructions:
            extra = text[pc+3:pc+3+size]
            addr = '{:04x}'.format(pc+0x1000)
            mnem = instructions[ins](pc+0x1000, ins, text[pc+1], extra)
            h = text[pc:pc+3+size].encode('hex')
            h = h.rjust(20)
            print '{}\t{}\t{}'.format(addr, h, mnem)
        else:
            print pc, ins, size
        #print text[pc:pc+size+3].encode('hex')

        pc += size + 3

    print '\n\n'
    data = body[page2_offset:page2_offset+page2_size]
    i = 0
    sys.stdout.write('{:x}\tdb "'.format(0x2000))
    written = False
    while i < page2_size:
        c = data[i]
        if c in string.letters+string.digits+string.punctuation+' ':
            sys.stdout.write(c)
            written = True
        else:
            if written:
                print '", 0x{:x}'.format(ord(c))
            else:
                print '0x{:x}'.format(ord(c))
            print '{:x}\tdb "'.format(0x2000+i+1),
            written = False
        i += 1
