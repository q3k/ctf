import z3

with open('crap.txt') as f:
    d = f.read()

key = z3.BitVec('key', 320)

var = {}

def NAND(a, b):
    z3._check_bv_args(a, b)
    a, b = _coerce_exprs(a, b)
    return z3.BitVecRef(Z3_mk_bvnand(a.ctx_ref(), a.as_ast(), b.as_ast()), a.ctx)

for line in d.split('\n')[::-1]:
    line = line.strip()
    if not line:
        continue

    left, right = line.split('=')
    left = left.strip()
    right = right.strip()

    if right.startswith('key'):
        bit = int(right.split('[')[1].split(']')[0])
        var[left] = (key >> bit) & 1
    else:
        operation = right.split('(')[0]
        operands = right.split('(')[1].split(')')[0].split(',')
        operands = [o.strip() for o in operands]
        if operation == 'AND2X2':
            var[left] = var[operands[0]] & var[operands[1]]
        elif operation == 'INVX1':
            var[left] = ~var[operands[0]]
        elif operation == 'NAND2X1':
            var[left] = ~(var[operands[0]] & var[operands[1]])
        elif operation == 'NAND3X1':
            var[left] = ~(var[operands[0]] & var[operands[1]] & var[operands[2]])
        elif operation == 'NOR2X1':
            var[left] = ~(var[operands[0]] | var[operands[1]])
        elif operation == 'NOR3X1':
            var[left] = ~(var[operands[0]] | var[operands[1]] | var[operands[2]])
        elif operation == 'OR2X2':
            var[left] = (var[operands[0]] | var[operands[1]])
        else:
            print operation
            raise 'fdsa'

s = z3.Solver()
s.add(var['unlocked'] == True)

print s.check()
model = s.model()

flag_int = int(str(model[key]))
flag_str = hex(flag_int)[2:-1].decode('hex')
print flag_str
