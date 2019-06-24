Minetest
========

A Google CTF 2019 Quals challenge.

Challenge Description
-----------

    I've stumbled upon this weird minetest map, can you make sense out of it?
    Minetest + mesecons required Non-standard flag format (enter bits as 0 and 1).

Solution
--------

We were given a [minetest](https://www.minetest.net/) world file. This world file used [mesecons](http://mesecons.net/) circuits to implement a big-ass logic circuit comprised out of levers (40 inputs), wires, gates (AND, OR, XOR, NOT) and a single lamp. You're supposed to figure out the required position of levers (on or off).

The world contained a pre-exported (?) file named `challenge.mts`. So of course, I wrote a tool that convers this 'Minetest Schema' into a Verilog netlist, and then used formal methods (SymbiYosys's `cover property`) statement to figure out the required inputs.

The solver is typical shite CTF-quality code. After loading the world into a hashmap in memory, it:

   - does a DFS starting from the lamp to establish inter-connected neighbours of circuit elements (ie. anything that can possibly connect is treated as neighbours). This gives us basic routing information.
   - 'joins' elements across eachother as it does the search - this does basic work of building nets out of wire segments, and establishes connectivity information to gates (eg. what net connects to what gate and what role does that net play in this gate)
   - does another iteration on the now built circuit, but this time treating nets as hyperedges of a connectivity graph of gates, levers and the lamp
   - exports a netlist in Verilog

This could've probably done in a single DFS pass if I thought of keeping track of sinks/sources at the same time, but I opted for the slower-but-safer approach (the code does quite a bit of sanity checks).

Once we have the exported netlist in Verilog, we can use a simple cover statement:

    cover property(lamp_1_1938);

And run SymbiYosys on the verilog netlist:

    sby cover.sby
    [...]
    SBY  2:06:00 [cover] engine_0: ##   0:00:00  Solver: yices
    SBY  2:06:00 [cover] engine_0: ##   0:00:00  Checking cover reachability in step 0..
    SBY  2:06:01 [cover] engine_0: ##   0:00:01  Reached cover statement at out2.v:3325 in step 0.
    SBY  2:06:01 [cover] engine_0: ##   0:00:01  Writing trace to VCD file: engine_0/trace0.vcd
    SBY  2:06:01 [cover] engine_0: ##   0:00:01  Writing trace to Verilog testbench: engine_0/trace0_tb.v
    SBY  2:06:01 [cover] engine_0: ##   0:00:01  Writing trace to constraints file: engine_0/trace0.smtc
    SBY  2:06:01 [cover] engine_0: ##   0:00:01  Status: PASSED

And recover the flag from the built sample testbench:

    $ grep 40\'b cover/engine_0/trace0_tb.v 
    PI_lever = 40'b1001100110000111110100111010001010100111;

After flipping bit order and wrapping the flag in the flag format burrito, we get the flag:

    CTF{1110010101000101110010111110000110011001}

