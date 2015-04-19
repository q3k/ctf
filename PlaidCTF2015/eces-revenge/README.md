ECE's Revenge 2
===============

A System Verilog source for a key checking module.

tl;dr - fix it up to work in a simulator like edaplayground.com (init_delay as an input to the adder was metastable, |'d it with init [before delay]). Then read key bits off m_o signal.
