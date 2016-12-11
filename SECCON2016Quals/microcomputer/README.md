Microcomputer
=============

H8/300H simulator running code that contains a debug monitor, which in turn speaks the GDB wire protocol.

Exploitation
------------

The stub doesn't let you control the PC register nor write to memory, so instead we exploit a bug in the command receiver to smash the registers to our liking. We thus redirect the CPU into an open() and a read() to get the flag contents into memory, then we dump it out using the memory read command.
