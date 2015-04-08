CodeGate Finals 2015 - strong\_arm (Pwn 1000)
=============================================

Aarch64 machine. And a /etc/motd that is sometimes a troll face, sometimes a dogeface, sometimes some other weird ASCII art.

... Wait, it's a symlink to /proc/motd..?!

Environment
-----------

We didn't get any binary or source for the kernel module (`motd`) that provided the procfs file. After some messing around, two observations were made:

 - `echo {0,1,2} > /proc/motd` will change the ASCII art that can be `cat`'d from it
 - `echo "A"x8 + "B"x8 + "C"x8 > /proc/motd` will make the kernel jump into 0x4343434343...

Exploit
-------

Based on the ret2dir attack. We simply return into shellcode from kernelmode - however, not to the usermode virtual memory directly, but into a physical mapped copy of it.

The shellcode is ran from a child processes. It will then traverse task structures to find its' own task struct, then its' parent's thask struct. Finally, it will overwrite its' parent creds with zeroes. Offsets for all this traversal have been found experimantally :).

Authors
-------

mak and q3k from Dragon Sector.
