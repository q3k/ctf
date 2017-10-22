from gdsii.library import Library
from gdsii.elements import *
from gdsii.structure import Structure

import json
import sys

with open('shiftreg_e7f285dccca5788b157d72e7fde31a92ed765c64ec86d56164426b7c1cde1625.gds2', 'rb') as stream:
    lib = Library.load(stream)

sr = lib[-1]

layernames = {
    41: 'pwell',

    49: 'metal1',
    50: 'via',
    51: 'metal2',
    61: 'via2',
    62: 'metal3',
    30: 'via3',
    31: 'metal4',

    81: 'pin',
}
layernumbers = {v:k for k, v in layernames.iteritems()}
m1, v1, m2, v2, m3, v3, m4 = [layernumbers[i] for i in 'metal1 via metal2 via2 metal3 via3 metal4'.split()]

boundaries_by_layer = {}

class BoundingBox(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    def __repr__(self):
        return '<BoundingBox X:{}, Y:{}, W:{}, H:{}>'.format(self.x, self.y, self.w, self.h)

    def intersects(a, b):
        #return abs(a.x - b.x) * 2 <= (a.w + b.w) and abs(a.y - b.y) * 2 <= (a.h + b.h)
        return not (b.x > a.x2 or b.x2 < a.x or b.y > a.y2 or b.y2 < a.y)
    
    def contains(self, x, y):
        return self.x <= x and self.x+self.w >= x and self.y <= y and self.y+self.h >= y

class QuadTree(object):
    def __init__(self, bound):
        self.bound = bound
        self.nodes = [None for _ in range(4)]
        self.objects = []

    def add(self, o):
        if self.nodes[0] is None:
            self.objects.append(o)
            o.qnode = self
            if len(self.objects) > 10:
                self.split()
        else:
            q = self._which_quad(o)
            if q is None:
                self.objects.append(o)
                o.qnode = self
            else:
                self.nodes[q].add(o)
                o.qnode = self.nodes[q]

    def retrieve(self, b):
        ret = []
        if self.nodes[0] != None:
            q = self._which_quad(b)
            #if q is not None:
                #ret += self.nodes[q].retrieve(b)
            # BUG: couldn't get the quadtree to work properly, just recurse down :/
            ret += self.nodes[0].retrieve(b)
            ret += self.nodes[1].retrieve(b)
            ret += self.nodes[2].retrieve(b)
            ret += self.nodes[3].retrieve(b)
        ret += self.objects
        return ret

    def _which_quad(self, o):
        midx = self.bound.x + self.bound.w / 2
        midy = self.bound.y + self.bound.h / 2
        def _which_quad_point(x, y):
            if x < midx:
                if y <= midy:
                    return 0
                else:
                    return 1
            else:
                if y <= midy:
                    return 2
                else:
                    return 3

        #a = _which_quad_point(o.b.x, o.b.y)
        #b = _which_quad_point(o.b.x+o.b.w, o.b.y)
        #c = _which_quad_point(o.b.x+o.b.w, o.b.y+o.b.h)
        #d = _which_quad_point(o.b.x, o.b.y+o.b.h)
        #if a == b == c == d:
        #    return a

        #obx, oby, obw, obh = o.b.x - 1000, o.b.y - 1000, o.b.w + 2000 , o.b.h + 2000
        #obx, oby, obw, obh = o.b.x + 100, o.b.y + 100, o.b.w + 200 , o.b.h + 200
        obx, oby, obw, obh = o.b.x, o.b.y, o.b.w, o.b.h

        top = oby < midy and oby+obh< midy
        bottom = oby > midy
        left = obx < midx and obx+obw < midx
        right = obx > midx

        if top and left:
            return 0
        if bottom and left:
            return 1
        if top and right:
            return 2
        if bottom and right:
            return 3

        return None

    def split(self):
        new_objects = []
        bw, bh = self.bound.w/2, self.bound.h/2
        b1 = BoundingBox(self.bound.x, self.bound.y, bw, bh)
        b2 = BoundingBox(self.bound.x, self.bound.y+bh, bw, bh)
        b3 = BoundingBox(self.bound.x+bw, self.bound.y, bw, bh)
        b4 = BoundingBox(self.bound.x+bw, self.bound.y+bh, bw, bh)
        self.nodes = [QuadTree(b1), QuadTree(b2), QuadTree(b3), QuadTree(b4)]
        for o in self.objects:
            q = self._which_quad(o)
            if q is None:
                new_objects.append(o)
                continue
            self.nodes[q].add(o)
            o.qnode = self.nodes[q]
        self.objects = new_objects

class B(object):
    def __init__(self, o):
        self.o = o
        self.xy = o.xy[:]
        self.layer = o.layer
        self.calculate_bb()

    def calculate_bb(self):
        xs = set()
        ys = set()
        for p in self.xy[:4]:
            x, y = p
            xs.add(x)
            ys.add(y)
        xs = sorted(list(xs))
        ys = sorted(list(ys))
        minx, maxx = xs[0], xs[1]
        miny, maxy = ys[0], ys[1]

        x = minx - 100
        y = miny - 100
        w = (maxx-minx) + 200
        h = (maxy-miny) + 200
        self.b = BoundingBox(x, y, w, h)

    @property
    def real_b(self):
        return BoundingBox(self.b.x+100, self.b.y+100, self.b.w-200, self.b.h-200)

    def collides(self, other):
        return self.b.intersects(other.b)
    
    def __repr__(self):
        return '<B X:{}, Y:{}, W:{}, H:{}>'.format(self.b.x, self.b.y, self.b.w, self.b.h)

structures = {}
for elem in list(lib):
    if type(elem) != Structure:
        continue
    structures[elem.name] = elem

print structures


for elem in list(sr):
    if type(elem) != Boundary:
        continue
    if elem.layer not in layernames:
        print elem.layer
        continue
    if elem.layer not in boundaries_by_layer:
        boundaries_by_layer[elem.layer] = []
    boundaries_by_layer[elem.layer].append(B(elem))

class TechMap(object):
    def __init__(self, name, *pins):
        self.name = name
        self.pins = pins

cell_translations = {
    'CNLZ': TechMap('AND2X2', ('A', (400, 6600)), ('B', (2000, 8600)), ('Y', (5200, 8600))),
    'CUWR': TechMap('NAND2X1', ('A', (400, 5800)), ('B', (3600, 10600)), ('Y', (2000, 5200))),
    'DHEA': TechMap('INVX1', ('A', (400, 3800)), ('Y', (2000, 1200))),
    'EUCC': TechMap('INVX8', ('A', (400, 5800)), ('Y', (5200, 6600))),
    'GQDV': TechMap('FILL'),
    'KZBF': TechMap('BUFX2', ('A', (400, 7800)), ('Y', (3600, 1200))),
    'LDCZ': TechMap('DFFPOSX1', ('CLK', (1200, 6800)), ('D', (2600, 8600)), ('Q', (18000, 6200))),
    'RGJP': TechMap('NOR2X1', ('A', (400, 3800)), ('B', (3600, 8600)), ('Y', (2000, 6600))),
    'SSNP': TechMap('BUFX4', ('A', (400, 8600)), ('Y', (3600, 6600))),
    'TMRO': TechMap('NAND3X1', ('A', (400, 9800)), ('B', (2000, 8600)), ('C', (3600, 11800)), ('Y', (5200, 10600))),
    'TVEG': TechMap('OR2X2', ('A', (400, 3800)), ('B', (2000, 6600)), ('Y', (5200, 8600))),
    'ZAGR': TechMap('NOR3X1', ('A', (2000, 4600)), ('B', (3600, 6600)), ('C', (5200, 8600)), ('Y', (10000, 11200))),
}


cellcounter = {}
class MySRef(SRef):
    def __init__(self, o):
        self.angle = o.angle
        self.elflags = o.elflags
        self.mag = o.mag
        self.properties = o.properties
        self.strans = o.strans
        self.struct_name = o.struct_name
        self.xy = o.xy
        self.rotated = False
        self.flipped = False
        if self.strans not in [0, None]:
            if self.strans != 32768:
                raise Exception("angle of dangle")
            self.flipped = True
        if self.angle not in [0.0, 0, None]:
            if self.angle != 180.0:
                raise Exception("angle of meat")
            self.rotated = True
        self.structure = structures[elem.struct_name]

    def map(self, nets):
        self.pinmap = {}
        if self.struct_name not in cell_translations:
            raise Exception('Unknown tech {}'.format(self.struct_name))
            return
        self.tech = cell_translations[self.struct_name]
        if self.tech.name not in cellcounter:
            cellcounter[self.tech.name] = 0
        self.name = '{}_{:04d}'.format(self.tech.name, cellcounter[self.tech.name]).lower()
        cellcounter[self.tech.name] += 1
        for pin_name, (x, y) in self.tech.pins:
            if self.flipped:
                y = -y
            if self.rotated:
                x = -x
                y = -y
            x += self.xy[0][0]
            y += self.xy[0][1]
            self.pinmap[pin_name] = None
            found_nets = set()
            for net in nets:
                cont = True
                for element in net.elements:
                    if element.layer != m1:
                        continue
                    if element.contains(x, y):
                        found_nets.add(net)
            if len(found_nets) > 1:
                fn = list(found_nets)
                first, rest = fn[0], fn[1:]
                for r in rest:
                    first.join(r)
                self.pinmap[pin_name] = first
            elif len(found_nets) == 1:
                self.pinmap[pin_name]  = list(found_nets)[0]

            self.pinmap[pin_name].cells.add((self, pin_name))
            if self.pinmap[pin_name] is None:
                print 'Floating pin', self.name, pin_name

    def __repr__(self):
        pins = ', '.join('{}: {}'.format(k, v) for k, v in self.pinmap.iteritems())
        return '<Cell {}, {}>'.format(self.name, pins)



cell_rows = {}
all_cells = []
for elem in list(sr):
    if type(elem) != SRef:
        continue
    elem = MySRef(elem)
    #print elem.angle, elem.elflags, elem.mag, elem.properties, elem.strans, elem.struct_name
    _, y = elem.xy[0]
    if y not in cell_rows:
        cell_rows[y] = []
    cell_rows[y].append(elem)
    all_cells.append(elem)

print 'Cell rows:', cell_rows.keys()

for row, cells in cell_rows.iteritems():
    for cell in cells:
        #if cell.flipped:
        #    continue
        s = cell.structure
        for elem in list(s):
            if type(elem) != Boundary:
                continue
            b = B(elem)
            newxy = []
            for x, y in b.xy:
                if cell.flipped:
                    y = -y
                if cell.rotated:
                    x = -x
                    y = -y
                x += cell.xy[0][0]
                y += cell.xy[0][1]
                newxy.append((x, y))
            b.xy = newxy
            b.calculate_bb()
            if b.layer not in boundaries_by_layer:
                continue
            boundaries_by_layer[b.layer].append(b)
print 'Instantiated cells.'



print 'metal1 boundaries', len(boundaries_by_layer[m1])
print 'metal2 boundaries', len(boundaries_by_layer[m2])
print 'metal3 boundaries', len(boundaries_by_layer[m3])
print 'metal4 boundaries', len(boundaries_by_layer[m4])

segcounter = 0
class Segment(object):
    def __init__(self, r):
        self.e = [r, ]
        global segcounter
        self.name = 'gen{:08d}'.format(segcounter)
        segcounter += 1

    def collides(self, other):
        return self.e[0].collides(other.e[0])

    def consume(self, otherseg):
        self.e += otherseg.e
        realnames = set()
        for s in [self, otherseg]:
            if s.name.startswith('gen'):
                continue
            realnames.add(s.name)
        if realnames:
            self.name = '_'.join(list(realnames))

named = {
    (186900, 350400): "clock",
    (263700, 384400): "unlocked",
    (-1900, 269700): "in",
    (407200, 0): "vdd",
    (258400, 0): "gnd",
}

class Segmenter(object):
    def __init__(self, stackup, layers):
        self.s = stackup
        self.metal = [self.s[0], self.s[2], self.s[4], self.s[6]]
        self.l = layers
        self.sl = {}
        self.slc = {}

    def segmentize_metal(self, m):
        self.sl[m] = []

        bminx, bmaxx = None, None
        bminy, bmaxy = None, None
        for elem in self.l[m]:
            if bminx is None or elem.b.x < bminx:
                bminx = elem.b.x
            if bminy is None or elem.b.y < bminy:
                bminy = elem.b.y
            if bmaxx is None or elem.b.x > bmaxx:
                bmaxx = elem.b.x
            if bmaxy is None or elem.b.y > bmaxy:
                bmaxy = elem.b.y

            name = named.get((elem.real_b.x, elem.real_b.y))
            seg = Segment(elem)
            if name is not None:
                print 'Found segment', name
                seg.name = name
            self.sl[m].append(seg)
            self.slc[elem] = self.sl[m][-1]

        bb = BoundingBox(bminx, bminy, bmaxx-bminx, bmaxy-bminy)
        print layernames[m], bb
        self.q = QuadTree(bb)

        for elem in self.l[m]:
            self.q.add(elem)

        changed = None
        while changed != 0:
            changed = 0
            allsegs = len(self.sl[m])
            i = 0
            done_this_round = set()
            for seg in self.sl[m]:
                i += 1
                sys.stdout.write('{}/{}\r'.format(i, allsegs))
                sys.stdout.flush()
                for elem in seg.e:
                    if elem in done_this_round:
                        continue
                    done_this_round.add(elem)
                    possible_colliders = set(elem.qnode.retrieve(elem))
                    #possible_colliders = set(self.l[m])
                    possible_colliders.remove(elem)
                    for pc in possible_colliders:
                        otherseg = self.slc[pc]
                        if seg != otherseg and elem.collides(pc):
                            changed += 1
                            seg.consume(otherseg)
                            for e in otherseg.e:
                                self.slc[e] = seg
                            del self.sl[m][self.sl[m].index(otherseg)]
                            break
            print 'Joined {} segments...'.format(changed)
        print max(len(s.e) for s in self.sl[m])

    def segmentize(self, f):
        for m in self.metal:
            self.segmentize_metal(m)

        layers = {}
        for layer, segments in self.sl.iteritems():
            layers[layer] = []
            for segment in segments:
                s = {}
                s['name'] = segment.name
                s['e'] = []
                for element in segment.e:
                    b = element.real_b
                    x, y, w, h = b.x, b.y, b.w, b.h
                    s['e'].append((x, y, w, h))
                layers[layer].append(s)
        json.dump(layers, f)


s = Segmenter([m1, v1, m2, v2, m3, v3, m4], boundaries_by_layer)
with open('segments.json', 'w') as f:
    s.segmentize(f)

class NetElement(BoundingBox):
    def __init__(self, x, y, w, h, layer):
        super(NetElement, self).__init__(x, y, w, h)
        self.layer = layer

class Net(object):
    def __init__(self, name, elements, start_layer):
        self.name = name
        self.elements = [NetElement(x, y, w, h, start_layer) for x, y, w, h in elements]
        self.vias = []
        self.nc = None
        self.cells = set()

    def join(self, other):
        self.vias = list(set(self.vias) | set(other.vias))
        self.elements = list(set(self.elements) | set(other.elements))
        realnames = set()
        if not self.name.startswith('gen'):
            realnames.add(self.name)
        if not other.name.startswith('gen'):
            realnames.add(other.name)
        if realnames:
            self.name = '_'.join(list(realnames))
        for (cell, pin_name) in other.cells:
            cell.pinmap[pin_name] = self
            self.cells.add((cell, pin_name))
        self.nc.nets.remove(other)

    def __repr__(self):
        return '<Net {}>'.format(self.name)

with open('segments.json') as f:
    data = json.load(f)

class NetConnector(object):
    def __init__(self, nets, adjacency):
        self.nets = nets
        self.adj = self._get_adjacent_vias(adjacency)
        for net in self.nets:
            net.nc = self

    def _get_adjacent_vias(self, adj):
        res = {}
        for a in adj:
            layer = a[0]
            via_layers = a[1:]
            res[layer] = []
            for via_layer in via_layers:
                res[layer] += boundaries_by_layer[via_layer]
        return res

    def connect(self, f):
        print 'Matching vias to nets...'
        for net in self.nets:
            for element in net.elements:
                possible_vias = self.adj[element.layer]
                for via in possible_vias:
                    if element.intersects(via.b):
                        net.vias.append(via)
        
        print 'Joining nets cross-metal...'
        changed = None
        via_to_net = {}
        while changed != 0:
            changed = 0
            for net in self.nets:
                cont = True
                for via in net.vias:
                    if via not in via_to_net:
                        via_to_net[via] = net
                        continue
                    if via_to_net[via] == net:
                        continue
                    changed += 1
                    other_net = via_to_net[via]
                    net.join(other_net)
                    for v2 in other_net.vias:
                        via_to_net[v2] = net
                    via_to_net[via] = net

                    cont = False
                    break
                if not cont:
                    break
            sys.stdout.write('{} nets...\r'.format(len(self.nets)))
            sys.stdout.flush()
        print len(self.nets), 'unique nets'

        for cell in all_cells:
            cell.map(nets)

        data = []
        for net in nets:
            n = {}
            n['name'] = net.name
            n['e'] = [(e.x, e.y, e.w, e.h) for e in net.elements]
            data.append(n)
        json.dump(data, f)



nets = set()
for layer, segments in data.iteritems():
    layer = int(layer)
    for segment in segments:
        name = segment['name']
        elements = segment['e']
        nets.add(Net(name, elements, layer))

nc = NetConnector(nets, [(m1, v1), (m2, v1, v2), (m3, v2, v3), (m4, v3)])

with open('nets.json', 'w') as f:
    nc.connect(f)

for net in nc.nets:
    if 'unlocked' in net.name:
        print net

renames = {
    'gen00053908': 'next',
}

print 'Running manual renames...'
for net in nc.nets:
    if net.name in renames:
        net.name = renames[net.name]


bufnames = {}

print 'Propagating buffers...'
changed = None
while changed != 0:
    changed = 0
    for cell in all_cells:
        if not cell.tech.name.startswith('BUF'):
            continue
        a = cell.pinmap['A']
        y = cell.pinmap['Y']
        if a == y:
            print 'Loop?', cell, a, y
            continue
        #print 'Removing', cell
        a.join(y)
        del all_cells[all_cells.index(cell)]
        changed += 1
        #aname = a.name.split('_')[0]
        #if aname.startswith('gen'):
        #    continue
        #if aname not in bufnames:
        #    bufnames[aname] = 1
        #y.name = '{}_buf{}'.format(aname, bufnames[aname])
        #bufnames[aname] += 1
    print changed, 'buffers removed.'

net_in = None
for net in nc.nets:
    if net.name == 'in':
        net_in = net
        break
print 'Discovering shift register stages...'

stages = []
cur = net_in
while True:
    next_ = None
    for cell, pin_name in cur.cells:
        print 'and?', cell
        if pin_name in ['A', 'B'] and cell.tech.name == 'AND2X2':
            other_pin_name = 'A' if pin_name == 'B' else 'B'
            if cell.pinmap[other_pin_name].name != 'next':
                continue

            y = cell.pinmap['Y']
            for cell2, pin_name2 in y.cells:
                print 'flop?', cell2
                if cell2.tech.name == 'DFFPOSX1' and pin_name2 == 'D':
                    next_ = cell2.pinmap['Q']
                    break
            if next_ is not None:
                break
        if cell.tech.name == 'INVX1' and pin_name == 'A':
            inv_out = cell.pinmap['Y']
            for cell2, pin_name2 in inv_out.cells:
                print 'nor?', cell2, pin_name2
                if cell2.tech.name == 'NOR2X1' and pin_name2 in ['A', 'B']:
                    other_pin_name = 'A' if pin_name2 == 'B' else 'B'
                    y = cell2.pinmap['Y']
                    for cell3, pin_name3 in y.cells:
                        print 'flop?', cell3, pin_name3
                        if cell3.tech.name == 'DFFPOSX1' and pin_name3 == 'D':
                            next_ = cell3.pinmap['Q']
                            break
                    if next_ is not None:
                        break
            if next_ is not None:
                break
    if next_ is None:
        break
    cur = next_
    print 'next stage', next_
    stages.append(next_)

print 'Found', len(stages), 'stages'
stage_to_bitn = {}
for i, s in enumerate(stages):
    stage_to_bitn[s] = i

print 'Discovering combinatorial checks...'
net_unlocked = None
for net in nc.nets:
    if net.name == 'unlocked':
        net_unlocked = net


seen = set()
def _recurse(c):
    if c in stage_to_bitn:
        stage_id = stage_to_bitn[c]
        v = 'key[{}]'.format(stage_id)
        print '{} = {}'.format(c.name, v)
        return v

    source = None
    for cell, pin_name in c.cells:
        if pin_name == 'Y' and not cell.tech.name.startswith('BUF'):
            source = cell
            break
    operands, operation = None, None
    cell = source
    if cell is None:
        print 'no source for', c
        print c.cells
        raise 'fdasdfs'
    if cell in seen:
        print cell
        raise Exception('loop?')
    seen.add(cell)

    args = ', '.join([v.name for k, v in cell.pinmap.iteritems() if k != 'Y'])
    print '{} = {}({})'.format(c.name, cell.tech.name, args)
    if cell.tech.name.startswith('NOR2'):
        a = _recurse(cell.pinmap['A'])
        b = _recurse(cell.pinmap['B'])
        operands = (a, b)
        operation = 'NOR'
    elif cell.tech.name.startswith('NOR3'):
        a = _recurse(cell.pinmap['A'])
        b = _recurse(cell.pinmap['B'])
        c = _recurse(cell.pinmap['C'])
        operands = (a, b, c)
        operation = 'NOR'
    elif cell.tech.name.startswith('OR'):
        a = _recurse(cell.pinmap['A'])
        b = _recurse(cell.pinmap['B'])
        operands = (a, b)
        operation = 'OR'
    elif cell.tech.name.startswith('NAND2'):
        a = _recurse(cell.pinmap['A'])
        b = _recurse(cell.pinmap['B'])
        operands = (a, b)
        operation = 'NAND'
    elif cell.tech.name.startswith('NAND3'):
        a = _recurse(cell.pinmap['A'])
        b = _recurse(cell.pinmap['B'])
        c = _recurse(cell.pinmap['C'])
        operands = (a, b, c)
        operation = 'NAND'
    elif cell.tech.name.startswith('AND'):
        a = _recurse(cell.pinmap['A'])
        b = _recurse(cell.pinmap['B'])
        operands = (a, b)
        operation = 'AND'
    elif cell.tech.name.startswith('INV'):
        a = _recurse(cell.pinmap['A'])
        operands = (a, )
        operation = 'NOT'
    else:
        raise Exception("Can't symbolize {}".format(cell))

    return (operation, operands)
    

top = _recurse(net_unlocked)

with open('netlist.v', 'w') as f:
    f.write('module shiftreg(\n')
    f.write('    output wire unlocked,\n')
    f.write('    input wire clock,\n')
    f.write('    input wire in\n')
    f.write(');\n\n')

    f.write('// autogenerated nets\n')
    for net in nc.nets:
        f.write('wire {};\n'.format(net.name))
    f.write('\n\n')

    f.write('// mapped cells\n')
    for cell in all_cells:
        pins = [(k, v.name) for k, v in cell.pinmap.iteritems()]
        pindef = ', '.join('.{}({})'.format(k, v) for k, v in pins)
        f.write('{} {}({});\n'.format(cell.tech.name, cell.name, pindef))
    f.write('\n\n')

    f.write('endmodule;\n')
