#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

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

void bb_getmynumber(int fd)
{
    uint32_t req = 0;
    uint8_t resp[8];
    if (send(fd, &req, 4, 0) <= 0)
    {
        printf("Could not send (%s).\n", strerror(errno));
        //return;
    }
    if(recv(fd, resp, 8, 0) != 8)
    {
        printf("Could not receive\n");
        return;
    }

    printf("phone number is %i\n", *((uint32_t *)(resp+4)));
}

void bb_getsms(int fd)
{
    uint32_t req = 6;
    uint8_t resp[512];
    send(fd, &req, 4, 0);
    if(recv(fd, resp, (161+8), 0) != (161+8))
    {
        printf("Could not receive\n");
        return;
    }
    printf("%s\n", resp+8);
}

int main(int argc, char **argv)
{
    int rpc = rpcsock();
    uint32_t send_size;
    read(0, &send_size, 4);
    uint8_t *send_buffer = (uint8_t *)malloc(send_size);
    read(0, send_buffer, send_size);
    uint32_t recv_size;
    read(0, &recv_size, 4);
    uint8_t *recv_buffer = (uint8_t *)malloc(recv_size);

    send(rpc, send_buffer, send_size, 0);
    if (recv(rpc, recv_buffer, recv_size, 0) != recv_size)
    {
        fprintf(stderr, "Error receiving data.\n");
        return 1;
    }

    write(1, recv_buffer, recv_size);
}
