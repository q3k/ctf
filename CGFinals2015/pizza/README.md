CodeGate Finals 2015 - Pizza (pwn 600)
======================================

This task was made up of a server that parsed PCAP files for clients. It had two main vunerabilities:

 - buffer overflow when receiving 74 bytes of payload filter into 20 byte buffer
 - info leak when showing TCP packets - all bytes from packet were shown, even if not actually present in the PCAP

Exploit
-------

This is pretty convoluted, as it was pretty late when I was solving this. First, we got a mem leak via the second vuln and got the stack cookie and address of the packet buffer in memory. Afterwards, we smash the stackvia the payload filter overflow, overwrite the canary with what we leaked, and overwrite the return address with a stack pivot towards a ROP in the packet data we sent earlier.

This 2nd stage ROP leaks printf in GOT.PLT, which is then used by the exploit client to calculate the address of system in libc. Then things get weird. Since we can't really easily call a read-from-client-into-memory function (lack of rdx manipulating gadgets), we jump into a gadet that first calls fgets() and then calls atoi(). We use fgets to overwrite `pcap\_open\_offline` in GOT.PLT. Earlier, we used three sprintf calls to overwrite `atoi` in GOT.PLT to point to a `pop rdi` shell. This lets us return from the fgets call into the chain. Additionally, we also re-call the program's `main()` after the `printf` in GOT.PLT leak in order to populate address filter buffers with usefule values (source for sprintf, and `sh\x00\x00`). Finally, we return into `pcap_open_offline`, which is now system.

Oh, and there are some `ntohl` calls in the chain to make sure that `(s)printf` calls run with `eax` = 0. Otherwise, weird crashes due to XMM register preserving occur.
