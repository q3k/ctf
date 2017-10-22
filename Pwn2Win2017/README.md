ShiftRegister
=============

Warning: Это Говнокод.

The task was to reverse an AMI0.35um VLSI mask. The chip was a simple SIPO shift register with an internal combinatorial network that would compare the state of the shift register and output a logical 1 if the data was correct.

I wrote all the stack to perform this from scratch, here's a short howto (blogpost incoming):

Run `extract.py` to generate segments per layer (`segments.json`), then nets (`nets.json`), then map cells and create netlist (`netlist.v`) and dump pseudocode assignements of shift register data comparison combinatorial logic. You can comment out the invocation of segmenter.segment() to skip the slowest part of the process and continue the second half of the process (net creation) from `segments.json`.

You can render the segments and nets to SVG via `render{nets,segments}.py`.

Feed the assignements to `solve.py` via `crap.txt` to get the flag.
