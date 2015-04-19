Prodmanager
===========

Pwn, 180 points

Bug
---

Use after free - product can be deleted but stays in price manager.

Exploit
-------

Free a node in a tree, allocate a buffer that has pointers to flag buffer as tree children. Dump nodes.

Authors
-------

Kalmar - bug discovery, RE, exploit
q3k - RE, exploit
