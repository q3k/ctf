import struct
import zlib
import collections

f = open("/home/q3k/.minetest/worlds/real/schems/challenge.mts", "rb")

assert f.read(4) == b"MTSM"
version, sx, sy, sz = struct.unpack(">HHHH", f.read(8))
assert version == 1

#for y in range(sy):
#    prob, = struct.unpack('>H', f.read(2))
#    print(y, prob)

nids = {}
rnids = {}
nid_count, = struct.unpack('>H', f.read(2))
for i in range(nid_count):
    nlen, = struct.unpack('>H', f.read(2))
    name = f.read(nlen).decode()
    print(i, name)
    nids[i] = name
    rnids[name] = i

world = {}

w = zlib.decompress(f.read())


air = rnids['air']
lever = rnids['mesecons_walllever:wall_lever_off']
lamp = rnids['mesecons_lamp:lamp_off']
wire = rnids['mesecons_insulated:insulated_off']
corner = rnids['mesecons_extrawires:corner_off']
crossover = rnids['mesecons_extrawires:crossover_off']
tjunction = rnids['mesecons_extrawires:tjunction_off']
gand = rnids['mesecons_gates:and_off']
gor = rnids['mesecons_gates:or_off']
gnot = rnids['mesecons_gates:not_off']
gxor = rnids['mesecons_gates:xor_off']

nuid = 0
class Net:
    def __init__(self, segments):
        global nuid
        self.segments = set(segments)
        self.uid = nuid
        nuid += 1

    def __repr__(self):
        return '<net {}>'.format(self.uid)

    def join(self, other):
        if self == other:
            return
        if len(self.segments) > len(other.segments):
            for segment in other.segments:
                segment.update_net(other, self)
            self.segments |= other.segments
        else:
            for segment in self.segments:
                segment.update_net(self, other)
            other.segments |= self.segments

    def connected(self):
        #print('Net.connected', self)
        c = set()
        for s in self.segments:
            c |= set(s.connected_with(self))
        res = set()
        for el in c:
            if el.nid != crossover:
                res.add(el)
        return res


class Node:
    @classmethod
    def make(cls, x, y, z, nid):
        kls = nid_map.get(nid, cls)
        return kls(x, y, z, nid)

    def __init__(self, x, y, z, nid):
        self.x = x
        self.y = y
        self.z = z
        self.nid = nid

    @property
    def neighbours(self):
        return []

    @property
    def name(self):
        return nids[self.nid]

    def __repr__(self):
        return '<node {} @{},{},{}, p1 {}, p2 {}>'.format(self.name, self.x, self.y, self.z, self.param1, self.param2)

    def join(self, other):
        return

    def build_netlist(self, f):
        raise NotImplemented

    def rel(self, other):
        return other.x - self.x, other.z - self.z

    def driving_node(self, _):
        return self

    def has_net(self, net):
        return False

class NodeGate3(Node):
    """AND, OR"""
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.source = None
        self.sinks = set()

    @property
    def neighbours(self):
        assert self.param1 == 0
        assert self.param2 == 3

        return [
            (self.x, self.z+1),
            (self.x, self.z-1),
            (self.x+1, self.z),
            (self.x-1, self.z),
        ]

    @property
    def sources(self):
        return set([self.source])

    def join(self, other):
        relx, relz = self.rel(other)
        if relx == 0 and relz == 1:
            assert self.source == None or self.source == other
            self.source = other
        else:
            self.sinks.add(other)
            assert len(self.sinks) <= 3

    @property
    def netlist_lvalue(self):
        return 'gate3_{}_{}'.format(self.x, self.z)

    def build_netlist(self, f):
        assert len(self.sinks) in [2, 3]
        form = None
        sinks = [s.driving_node(self) for s in self.sinks]
        if self.nid == gand:
            form = " & ".join(s.netlist_lvalue for s in sinks)
        else:
            form = " | ".join(s.netlist_lvalue for s in sinks)
        f.write("assign {} = {};\n".format(self.netlist_lvalue, form))
        return sinks

class NodeGate2(Node):
    """XOR"""
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.source = None
        self.sinks = set()

    @property
    def sources(self):
        return set([self.source])

    @property
    def neighbours(self):
        assert self.param1 == 0
        assert self.param2 == 3

        return [
            (self.x, self.z+1),
            (self.x+1, self.z),
            (self.x-1, self.z),
        ]

    def join(self, other):
        relx, relz = self.rel(other)
        if relx == 0 and relz == 1:
            assert self.source == None or self.source == other
            self.source = other
        else:
            self.sinks.add(other)
            assert len(self.sinks) <= 3

    @property
    def netlist_lvalue(self):
        return 'xor_{}_{}'.format(self.x, self.z)

    def build_netlist(self, f):
        assert len(self.sinks) == 2
        sinks = [s.driving_node(self) for s in self.sinks]
        form = " ^ ".join(s.netlist_lvalue for s in sinks)
        f.write("assign {} = {};\n".format(self.netlist_lvalue, form))
        return sinks


class NodeGate1(Node):
    """NOT"""
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.source = None
        self.sink = None

    @property
    def sinks(self):
        return set([self.sink])
    @property
    def sources(self):
        return set([self.source])

    @property
    def neighbours(self):
        assert self.param1 == 0
        assert self.param2 == 3

        return [
            (self.x, self.z+1),
            (self.x, self.z-1),
        ]

    def join(self, other):
        relx, relz = self.rel(other)
        if relx == 0 and relz == 1:
            assert self.source == None or self.source == other
            self.source = other
        else:
            assert self.sink == None or self.sink == other
            self.sink = other

    @property
    def netlist_lvalue(self):
        return 'not_{}_{}'.format(self.x, self.z)

    def build_netlist(self, f):
        sink = self.sink.driving_node(self)
        f.write("assign {} = ~{};\n".format(self.netlist_lvalue, sink.netlist_lvalue))
        return [sink]

class NodeWire(Node):
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.net = Net([self])
        self.connected = set()

    def update_net(self, old_net, new_net):
        assert self.net in (old_net, new_net)
        self.net = new_net

    def has_net(self, net):
        return self.net == net

    def connected_with(self, net):
        return self.connected

    @property
    def neighbours(self):
        assert self.param1 ==0
        if self.param2 == 0:
            return [
                (self.x+1, self.z),
                (self.x-1, self.z),
            ]
        elif self.param2 == 3:
            return [
                (self.x, self.z+1),
                (self.x, self.z-1),
            ]
        else:
            raise '???'

    def join(self, other):
        if other.nid in [wire, corner, tjunction]:
            self.net.join(other.net)
        else:
            self.connected.add(other)

    def driving_node(self, _):
        connected = self.net.connected()

        drivers = set()
        for c in connected:
            for s in c.sources:
                if s.has_net(self.net):
                    drivers.add(c)

        #print('Driving node {} -> {}'.format(self, drivers))
        assert len(drivers) == 1
        return list(drivers)[0]

class NodeCorner(Node):
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.net = Net([self])
        self.connected = set()

    def update_net(self, old_net, new_net):
        assert self.net in (old_net, new_net)
        self.net = new_net

    def has_net(self, net):
        return self.net == net

    def connected_with(self, net):
        return self.connected

    @property
    def neighbours(self):
        assert self.param1 ==0
        if self.param2 == 0:
            return [
                (self.x, self.z-1),
                (self.x-1, self.z),
            ]
        elif self.param2 == 1:
            return [
                (self.x, self.z+1),
                (self.x-1, self.z),
            ]
        elif self.param2 == 2:
            return [
                (self.x, self.z+1),
                (self.x+1, self.z)
            ]
        elif self.param2 == 3:
            return [
                (self.x, self.z-1),
                (self.x+1, self.z),
            ]
        else:
            raise '???'

    def join(self, other):
        if other.nid in [wire, corner, tjunction]:
            self.net.join(other.net)
        else:
            self.connected.add(other)

    def driving_node(self, _):
        connected = self.net.connected()

        drivers = set()
        for c in connected:
            for s in c.sources:
                if s.has_net(self.net):
                    drivers.add(c)

        #print('Driving node {} -> {}'.format(self, drivers))
        assert len(drivers) == 1
        return list(drivers)[0]


class NodeCrossover(Node):
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.nets = [Net([self]), Net([self])]
        self.connected = [set(), set()]

    def connected_with(self, net):
        i = self.nets.index(net)
        return self.connected[i]

    def update_net(self, old_net, new_net):
        found = False
        for i, n in enumerate(self.nets):
            if n == old_net:
                self.nets[i] = new_net
                found = True
            elif n == new_net:
                found = True
        assert found

    def has_net(self, net):
        return net in self.nets

    def net_for(self, other):
        relx, relz = self.rel(other)
        if relx == 0:
            assert relz in (-1, 1)
            return self.nets[0]
        elif relz == 0:
            assert relx in (-1, 1)
            return self.nets[1]
        else:
            raise '???'

    def driving_node(self, elem):
        for n in self.nets:
            connected = n.connected()
            if elem not in connected:
                continue

            drivers = set()
            for c in connected:
                for s in c.sources:
                    if s.has_net(n):
                        drivers.add(c)
            #print('Driving node {} ({}) -> {}'.format(self, n, drivers))
            assert len(drivers) == 1
            return list(drivers)[0]

        else:
            print(self, sink, self.nets, self.connected)
            raise '???'


    @property
    def neighbours(self):
        assert self.param1 == 0
        assert self.param2 == 3

        return [
            (self.x, self.z+1),
            (self.x, self.z-1),
            (self.x+1, self.z),
            (self.x-1, self.z),
        ]

    def join(self, other):
        relx, relz = self.rel(other)
        i = 0
        if relz == 0:
            i = 1
            assert relx in (-1, 1)
        else:
            assert relx == 0
            assert relz in (-1, 1)

        if other.nid in [wire, corner, tjunction]:
            other.net.join(self.nets[i])
        elif other.nid == crossover:
            other.net_for(self).join(self.nets[i])
        else:
            self.connected[i].add(other)
            assert len(self.connected[i]) <= 2


class NodeTJunction(Node):
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.net = Net([self])
        self.connected = set()

    def update_net(self, old_net, new_net):
        assert self.net in (old_net, new_net)
        self.net = new_net

    def has_net(self, net):
        return self.net == net

    def connected_with(self, net):
        return self.connected

    @property
    def neighbours(self):
        assert self.param1 ==0
        if self.param2 == 1:
            return [
                (self.x, self.z+1),
                (self.x, self.z-1),
                (self.x-1, self.z),
            ]
        elif self.param2 == 3:
            return [
                (self.x, self.z+1),
                (self.x, self.z-1),
                (self.x+1, self.z),
            ]
        else:
            raise '???'

    def join(self, other):
        if other.nid in [wire, corner, tjunction]:
            self.net.join(other.net)
        else:
            self.connected.add(other)

    def driving_node(self, _):
        connected = self.net.connected()

        drivers = set()
        for c in connected:
            for s in c.sources:
                if s.has_net(self.net):
                    drivers.add(c)

        #print('Driving node {} -> {}'.format(self, drivers))
        assert len(drivers) == 1
        return list(drivers)[0]

class NodeLever(Node):
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.source = None

    @property
    def sinks(self):
        return set()

    @property
    def sources(self):
        return set([self.source])


    @property
    def neighbours(self):
        assert self.param1 == 0
        assert self.param2 == 0

        return [
            (self.x, self.z+1),
        ]

    def join(self, other):
        assert self.source is None or self.source is other
        self.source = other

    @property
    def netlist_lvalue(self):
        return 'lever[{}]'.format(self.x)

    def build_netlist(self, f):
        return []

class NodeLamp(Node):
    def __init__(self, x, y, z, nid):
        super().__init__(x, y, z, nid)
        self.sink = None

    @property
    def sinks(self):
        return set([self.sink])
    @property
    def sources(self):
        return set()

    @property
    def neighbours(self):
        assert self.param1 == 0

        return [
            (self.x, self.z+1),
            (self.x, self.z-1),
            (self.x+1, self.z),
            (self.x-1, self.z),
        ]

    def join(self, other):
        assert self.sink is None or self.sink == other
        self.sink = other

    @property
    def netlist_lvalue(self):
        return 'lamp_{}_{}'.format(self.x, self.z)

    def build_netlist(self, f):
        sink = self.sink.driving_node(self)
        f.write("assign {} = {};\n".format(self.netlist_lvalue, sink.netlist_lvalue))
        return [sink]

nid_map = {
    gand: NodeGate3,
    gor: NodeGate3,
    gxor: NodeGate2,
    gnot: NodeGate1,
    wire: NodeWire,
    corner: NodeCorner,
    crossover: NodeCrossover,
    tjunction: NodeTJunction,
    lever: NodeLever,
    lamp: NodeLamp,

}


i = 0
for z in range(sz):
    for y in range(sy):
        for x in range(sx):
            content, = struct.unpack('>H', w[i:i+2])
            assert content in nids
            if x not in world:
                world[x] = {}
            if y not in world[x]:
                world[x][y] = {}

            world[x][y][z] = Node.make(x, y, z, content)
            i += 2

for z in range(sz):
    for y in range(sy):
        for x in range(sx):
            content, = struct.unpack('>B', w[i:i+1])
            world[x][y][z].param1 = content
            i += 1

for z in range(sz):
    for y in range(sy):
        for x in range(sx):
            content, = struct.unpack('>B', w[i:i+1])
            world[x][y][z].param2 = content
            i += 1

print("Schematic loaded.")

# Build indexes...

levers = []
lamps = []

for x in range(sx):
    for y in range(sy):
        for z in range(sz):
            n = world[x][y][z]
            if n.nid == air:
                continue
            if n.nid == lamp:
                lamps.append(n)
            if n.nid == lever:
                levers.append(n)

assert len(lamps) == 1
assert len(levers) == 40

print("Indices built.")

q = collections.deque()
q.append((None, lamps[0]))
seen = set()

def world_xyz(x, y, z):
    if x not in world:
        return
    if y not in world[x]:
        return
    if z not in world[x][y]:
        return
    return world[x][y][z]

while len(q) > 0:
    prev, el = q.pop()

    if el is None:
        continue

    k = (prev, el)
    if k in seen:
        continue
    seen.add(k)

    if el.nid == air:
        continue

    if prev is not None and prev.nid != air:
        prev.join(el)
        el.join(prev)


    for nx, nz in el.neighbours:

        neigh = world_xyz(nx, el.y, nz)
        dx = nx - el.x
        dz = nz - el.z
        if (dx, dz) not in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            raise Exception("unlikely neighbourhood: {} said {}".format(el, neigh))

        q.append((el, neigh))

print("Connectivity list built, visited {} elements".format(len(seen)))
print("Building netlist...")

q = collections.deque()
q.append(lamps[0])
seen = set()

f = open('out2.v', 'w')

while len(q) > 0:
    el = q.pop()
    if el in seen:
        continue
    seen.add(el)

    sources = el.build_netlist(f)
    for s in sources:
        q.append(s)
