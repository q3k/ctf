#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

struct rb_node
{
  char *name;
  uint64_t size;
  void *data;
  struct rb_node *child_left;
  struct rb_node *child_right;
  struct rb_node *parent;
  int red;
  int field_34;
} __attribute__((packed));

//-------------------------------------------------------------------------
// Function declarations

int init_proc(void); // weak
// void free(void *ptr);
// int puts(const char *s);
// size_t fread(void *ptr, size_t size, size_t n, FILE *stream);
// void setbuf(FILE *stream, char *buf);
// size_t malloc_usable_size(void *ptr);
// char *fgets(char *s, int n, FILE *stream);
// int strcmp(const char *s1, const char *s2);
// int __gmon_start__(void); weak
// void *malloc(size_t size);
// int _IO_getc(_IO_FILE *fp);
// void *realloc(void *ptr, size_t size);
// int __printf_chk(uint64_t a1, uint64_t a2, ...);
// unsigned uint64_t strtoul(const char *nptr, char **endptr, int base);
// void __noreturn exit(int status);
// size_t fwrite(const void *ptr, size_t size, size_t n, FILE *s);
// int __fastcall __cxa_finalize(uint64_t); weak
int  main(int argc, const char **argv, const char **envp);
struct rb_node *insert_row(struct rb_node *new_row);
void fuckitall();
char *get_until_newline();
char *stdin_get(char *a1, uint64_t a2);
size_t stdin_fread(void *a1, size_t a2);
void command_get();
void command_put();
struct rb_node *command_dump();
int command_del();
uint64_t rep();
int sub_1B30(unsigned int a1, uint64_t a2, uint64_t a3);
void term_proc();
// void free(void *ptr);
// int strcmp(const char *s1, const char *s2);
// int _printf_chk(uint64_t, uint64_t, ...);
// int ITM_deregisterTMCloneTable(void); weak
// int __fastcall Jv_RegisterClasses(uint64_t); weak

//-------------------------------------------------------------------------
// Data declarations

struct rb_node *g_Rows_Head;
// extern struct _IO_FILE *stdout;
// extern struct _IO_FILE *stdin;
// extern _UNKNOWN _cxa_finalize; weak
// extern _UNKNOWN _gmon_start__; weak


//----- (0000000000000B20) ----------------------------------------------------
int  main(int argc, const char **argv, const char **envp)
{
  struct rb_node *flagrow; // rbx@1
  char *v4; // rax@1
  void *v5; // rax@3

  setbuf(stdin, 0LL);
  setbuf(stdout, 0LL);
  flagrow = (struct rb_node *)malloc(56uLL);
  v4 = (char *)malloc(8uLL);
  if ( v4 )
    *(uint64_t *)v4 = 29049562776954996LL;        // th3fl4g
  flagrow->name = v4;
  v5 = malloc(9uLL);
  if ( v5 )
  {
    *((uint8_t *)v5 + 8) = 0;
    *(uint64_t *)v5 = 0xA68736977756F79LL;        // youwish\n
  }
  flagrow->data = v5;
  flagrow->size = 8LL;
  insert_row(flagrow);
  puts("INFO: Welcome to the PlaidDB data storage service.");
  puts("INFO: Valid commands are GET, PUT, DUMP, DEL, EXIT");
  while ( 1 )
    rep();
}


//----- (0000000000000CF0) ----------------------------------------------------
struct rb_node * insert_row(struct rb_node *new_row)
{
  struct rb_node *x_; // rbp@1
  struct rb_node *insert_iter_cur_node; // rbx@1
  char *name; // r13@2
  struct rb_node *iter_child; // rdx@4
  int v5; // eax@6
  struct rb_node *px; // rax@9
  struct rb_node *v7; // rax@11
  struct rb_node *v8; // rcx@11
  struct rb_node *v9; // rcx@13
  struct rb_node *v10; // rcx@14
  struct rb_node *ppx; // rdx@20
  struct rb_node *y; // rcx@20
  struct rb_node *right_ip_sibling; // rsi@24
  struct rb_node *v14; // rsi@26
  struct rb_node *v15; // rax@26
  struct rb_node *v16; // rcx@27
  struct rb_node *v17; // rcx@29
  struct rb_node *v18; // rcx@30
  struct rb_node *v19; // rcx@34
  struct rb_node *v20; // rcx@35
  struct rb_node *v21; // rcx@36
  struct rb_node *v22; // rcx@38
  struct rb_node *v24; // rax@45
  struct rb_node *v25; // rax@46
  struct rb_node *v26; // rax@47

  x_ = new_row;
  insert_iter_cur_node = g_Rows_Head;
  if ( !g_Rows_Head )
  {
    new_row->parent = 0LL;
    new_row->child_right = 0LL;
    px = 0LL;
    new_row->child_left = 0LL;
    new_row->red = 1;
    g_Rows_Head = new_row;
    goto LABEL_18;
  }
  name = new_row->name;
  while ( 1 )
  {
    v5 = strcmp(name, insert_iter_cur_node->name);
    if ( v5 >= 0 )
      break;
    iter_child = insert_iter_cur_node->child_left;
    if ( !iter_child )
    {
INSERT_AT_CHILD:
      new_row->parent = insert_iter_cur_node;
      new_row->child_right = 0LL;
      new_row->child_left = 0LL;
      new_row->red = 1;
      if ( v5 < 0 )
      {
        insert_iter_cur_node->child_left = new_row;
        px = insert_iter_cur_node;
        new_row = g_Rows_Head;
      }
      else
      {
        insert_iter_cur_node->child_right = new_row;
        px = insert_iter_cur_node;
        new_row = g_Rows_Head;
      }
LABEL_18:
      while ( 2 )
      {
        if ( !px || px->red != 1 )
        {
          g_Rows_Head = new_row;
          new_row->red = 0;
          return 0LL;
        }
        ppx = px->parent;
        y = ppx->child_left;                    // y <- aunt/uncle of x
        if ( y != px )                          // p[x] == left[p[p[x]]]
        {
          if ( y && y->red == 1 )               // if color[y] == RED
          {
            y->red = 0;                         // CASE 1: RECOLOR
            x_ = ppx;
            px->red = 0;
            ppx->red = 1;
CONTINUE_2_LEVELS_UP:
            px = x_->parent;                    // progress one level up
            continue;
          }
          if ( x_ != px->child_left )           // x = right[p[x]]
          {
LABEL_11:
            px->red = 0;
            v7 = ppx->child_right;              // CASE 2
            ppx->red = 1;
            v8 = v7->child_left;
            ppx->child_right = v8;
            if ( v8 )
              v8->parent = ppx;
            v9 = ppx->parent;
            v7->parent = v9;
            if ( v9 )
            {
              v10 = ppx->parent;
              if ( ppx == v10->child_left )
                v10->child_left = v7;
              else
                v10->child_right = v7;
            }
            else
            {
              new_row = v7;
            }
            v7->child_left = ppx;
            ppx->parent = v7;
            goto CONTINUE_2_LEVELS_UP;
          }
          v19 = x_->child_right;                // CASE 3
          px->child_left = v19;
          if ( v19 )
          {
            v19->parent = px;
            v20 = px->parent;
            x_->parent = v20;
            if ( v20 )
            {
LABEL_36:
              v21 = px->parent;
              if ( v21->child_left == px )
                v21->child_left = x_;
              else
                v21->child_right = x_;
            }
            else
            {
              new_row = x_;
            }
            v22 = x_;
            x_->child_right = px;
            px->parent = x_;
            x_ = px;
            px = v22;
            goto LABEL_11;
          }
          x_->parent = ppx;
          goto LABEL_36;
        }
        break;
      }
      right_ip_sibling = ppx->child_right;      // y2 <- left[p[p[x]]]
      if ( right_ip_sibling && right_ip_sibling->red == 1 )// if color[y] == RED
      {
        right_ip_sibling->red = 0;              // CASE 1: RECOLOR
        x_ = ppx;
        px->red = 0;
        ppx->red = 1;
        goto CONTINUE_2_LEVELS_UP;
      }
      v14 = y->child_right;
      v15 = ppx->child_left;
      if ( v14 != x_ )
      {
LABEL_27:
        y->red = 0;
        v16 = v15->child_right;
        ppx->red = 1;
        ppx->child_left = v16;
        if ( v16 )
          v16->parent = ppx;
        v17 = ppx->parent;
        v15->parent = v17;
        if ( v17 )
        {
          v18 = ppx->parent;
          if ( ppx == v18->child_left )
            v18->child_left = v15;
          else
            v18->child_right = v15;
        }
        else
        {
          new_row = v15;
        }
        v15->child_right = ppx;
        ppx->parent = v15;
        goto CONTINUE_2_LEVELS_UP;
      }
      v24 = x_->child_left;
      y->child_right = v24;
      if ( v24 )
      {
        v24->parent = y;
        v25 = y->parent;
        x_->parent = v25;
        if ( v25 )
        {
LABEL_47:
          v26 = y->parent;
          if ( y == v26->child_left )
            v26->child_left = v14;
          else
            v26->child_right = v14;
        }
        else
        {
          new_row = x_;
        }
        v14->child_left = y;
        x_ = y;
        y->parent = v14;
        v15 = ppx->child_left;
        y = v14;
        goto LABEL_27;
      }
      x_->parent = ppx;
      goto LABEL_47;
    }
CONTINUE_INSERT_ITER:
    insert_iter_cur_node = iter_child;
  }
  if ( v5 )
  {
    iter_child = insert_iter_cur_node->child_right;
    if ( !iter_child )
      goto INSERT_AT_CHILD;
    goto CONTINUE_INSERT_ITER;
  }
  return insert_iter_cur_node;
}

//----- (0000000000001020) ----------------------------------------------------
void fuckitall()
{
  puts("INFO: Goodbye");
  exit(0);
}

//----- (0000000000001040) ----------------------------------------------------
char *get_until_newline()
{
  char *result_buffer; // r12@1
  char *endptr; // rbx@1
  size_t usable_size; // r14@1
  char read_char; // al@3 MAPDST
  uint64_t used_len; // r13@5
  char *v6; // rax@6

  result_buffer = (char *)malloc(8uLL);
  endptr = result_buffer;
  usable_size = malloc_usable_size(result_buffer);
  while ( 1 )
  {
    read_char = _IO_getc(stdin);
    if ( read_char == -1 )
      fuckitall();
    used_len = endptr - result_buffer;
    if ( usable_size <= endptr - result_buffer )
    {
      v6 = (char *)realloc(result_buffer, 2 * usable_size);
      result_buffer = v6;
      if ( !v6 )
      {
        puts("FATAL: Out of memory");
        exit(-1);
      }
      endptr = &v6[used_len];
      usable_size = malloc_usable_size(v6);
    }
    if ( read_char == '\n' )
    {
      *endptr = 0;
      break;
    }
    *endptr++ = read_char;
  }
  return result_buffer;
}

//----- (0000000000001110) ----------------------------------------------------
char * stdin_get(char *a1, uint64_t a2)
{
  char *result; // rax@1

  result = fgets(a1, a2, stdin);
  if ( !result )
    fuckitall();
  return result;
}

//----- (0000000000001140) ----------------------------------------------------
size_t stdin_fread(void *a1, size_t a2)
{
  size_t result; // rax@1

  result = fread(a1, 1uLL, a2, stdin);
  if ( a2 > result )
    fuckitall();
  return result;
}

//----- (0000000000001170) ----------------------------------------------------
void command_get()
{
  char *row_key; // rbp@1
  struct rb_node *row; // rbx@1
  int v2; // eax@3

  puts("PROMPT: Enter row key:");
  row_key = get_until_newline();
  row = g_Rows_Head;
LABEL_2:
  if ( row )
  {
    while ( 1 )
    {
      v2 = strcmp(row_key, row->name);
      if ( v2 < 0 )
      {
        row = row->child_left;
        goto LABEL_2;
      }
      if ( !v2 )
        break;
      row = row->child_right;
      if ( !row )
        goto LABEL_6;
    }
    printf("INFO: Row data [%zd bytes]:\n", row->size);
    fwrite(row->data, 1uLL, row->size, stdout);
    free(row_key);
  }
  else
  {
LABEL_6:
    puts("ERROR: Row not found.");
    free(row_key);
  }
}

//----- (0000000000001240) ----------------------------------------------------
void command_put()
{
  struct rb_node *new_row; // rbx@1
  uint64_t v1; // rax@2
  void *v2; // rax@2
  struct rb_node *v3; // rbp@3
  uint64_t v4; // [sp+0h] [bp-38h]@2

  new_row = (struct rb_node *)malloc(0x38uLL);
  if ( !new_row )
    goto LABEL_10;
  puts("PROMPT: Enter row key:");
  new_row->name = get_until_newline();
  puts("PROMPT: Enter data size:");
  stdin_get((char *)&v4, 16LL);
  v1 = strtoul((const char *)&v4, 0LL, 0);
  new_row->size = v1;
  v2 = malloc(v1);
  new_row->data = v2;
  if ( !v2 )
  {
    puts("ERROR: Can't store that much data.");
    free(new_row->name);
      free(new_row);
      return;
LABEL_10:
    puts("FATAL: Can't allocate a row");
    exit(-1);
  }
  puts("PROMPT: Enter data:");
  stdin_fread(new_row->data, new_row->size);
  v3 = insert_row(new_row);
  if ( v3 )
  {
    free(new_row->name);
    free(v3->data);
    v3->size = new_row->size;
    v3->data = new_row->data;
    free(new_row);
    puts("INFO: Update successful.");
  }
  else
  {
    puts("INFO: Insert successful.");
  }
}

static void _recurse_tree(struct rb_node *node, uint8_t indent)
{
    for (uint8_t i = 0; i < indent; i++)
        printf("  ");
    if (node->red == 1)
        printf("RED [%s] @%p\n", node->name, node);
    else
        printf("BLK [%s] @%p\n", node->name, node);

    for (uint8_t i = 0; i < indent; i++)
        printf("  ");
    printf("`--> Left: ");
    if (node->child_left == 0)
        printf("NULL\n");
    else
    {
        printf("\n");
        _recurse_tree(node->child_left, indent+1);
    }

    for (uint8_t i = 0; i < indent; i++)
        printf("  ");
    printf("`--> Right: ");
    if (node->child_right == 0)
        printf("NULL\n");
    else
    {
        printf("\n");
        _recurse_tree(node->child_right, indent+1);
    }
}

void print_tree_debug(void)
{
    _recurse_tree(g_Rows_Head, 1);
}

//----- (00000000000013A0) ----------------------------------------------------
struct rb_node *command_dump()
{

    // HAAAX
    print_tree_debug();


  struct rb_node *result; // rax@1
  struct rb_node *v1; // rbx@1
  struct rb_node *v2; // rax@5

  puts("INFO: Dumping all rows.");
  result = (struct rb_node *)&g_Rows_Head;
  v1 = g_Rows_Head;
  if ( g_Rows_Head )
  {
    while ( v1->child_left )
      v1 = v1->child_left;
    while ( 1 )
    {
      while ( 1 )
      {
        printf("INFO: Row [%s], %zd bytes\n", v1->name, v1->size);
        v2 = v1->child_right;
        if ( !v2 )
          break;
        do
        {
          v1 = v2;
          v2 = v2->child_left;
        }
        while ( v2 );
      }
      result = v1->parent;
      if ( !result || v1 != result->child_left )
        break;
LABEL_15:
      v1 = result;
    }
    while ( result )
    {
      if ( v1 != result->child_right )
        goto LABEL_15;
      v1 = result;
      result = result->parent;
    }
  }
  return result;
}

//----- (0000000000001470) ----------------------------------------------------
int command_del()
{
  char *v0; // r12@1
  struct rb_node *v1; // rbx@1
  const char *v2; // rbp@3
  int v3; // eax@3
  struct rb_node *child_left; // rax@8
  struct rb_node *child_right; // rcx@9
  struct rb_node *v7; // rsi@14
  struct rb_node *v8; // rsi@20
  struct rb_node *v9; // rsi@23
  struct rb_node *v10; // rcx@26
  struct rb_node *v11; // rdi@30
  struct rb_node *v12; // rax@31
  struct rb_node *v13; // rsi@33
  struct rb_node *v14; // rcx@35
  struct rb_node *v15; // rcx@40
  struct rb_node *v16; // rax@42
  struct rb_node *v17; // rsi@44
  struct rb_node *v18; // rsi@45
  struct rb_node *v19; // rax@48
  struct rb_node *v20; // rcx@49
  struct rb_node *v21; // rsi@51
  struct rb_node *v22; // rcx@54
  struct rb_node *v23; // rsi@56
  struct rb_node *v24; // rsi@57
  struct rb_node *v25; // rdx@10
  int v26; // edi@10
  struct rb_node *v27; // rax@79
  struct rb_node *v28; // rax@81
  struct rb_node *v29; // rax@82
  struct rb_node *v30; // rax@87
  struct rb_node *v31; // rax@89
  struct rb_node *v32; // rax@90
  struct rb_node *v33; // rsi@102
  struct rb_node *v34; // rsi@104
  struct rb_node *v35; // rsi@105
  struct rb_node *v36; // rcx@107
  struct rb_node *v37; // rax@109
  struct rb_node *v38; // rax@111
  struct rb_node *v39; // rax@112

  puts("PROMPT: Enter row key:");
  v0 = get_until_newline();
  v1 = g_Rows_Head;
LABEL_2:
  if ( !v1 )
    return puts("ERROR: Row not found.");
  while ( 1 )
  {
    v2 = v1->name;
    v3 = strcmp(v0, v1->name);
    if ( v3 < 0 )
    {
      v1 = v1->child_left;
      goto LABEL_2;
    }
    if ( !v3 )
      break;
    v1 = v1->child_right;
    if ( !v1 )
      return puts("ERROR: Row not found.");
  }
  child_left = v1->child_left;
  if ( child_left )
  {
    child_right = v1->child_right;
    if ( child_right )
    {
      while ( child_right->child_left )
        child_right = child_right->child_left;
      child_left = child_right->child_right;
      v25 = child_right->parent;
      v26 = child_right->red;
      if ( child_left )
      {
        child_left->parent = v25;
        v7 = child_right->parent;
      }
      else
      {
        v7 = child_right->parent;
      }
      if ( v25 )
      {
        if ( child_right == v25->child_left )
          v25->child_left = child_left;
        else
          v25->child_right = child_left;
      }
      else
      {
        g_Rows_Head = child_left;
      }
      if ( v1 == v7 )
        v25 = child_right;
      child_right->child_left = v1->child_left;
      child_right->child_right = v1->child_right;
      child_right->parent = v1->parent;
      *(uint64_t *)&child_right->red = *(uint64_t *)&v1->red;
      v8 = v1->parent;
      if ( v8 )
      {
        if ( v8->child_left == v1 )
          v8->child_left = child_right;
        else
          v8->child_right = child_right;
      }
      else
      {
        g_Rows_Head = child_right;
      }
      v1->child_left->parent = child_right;
      v9 = v1->child_right;
      if ( v9 )
        v9->parent = child_right;
      if ( v25 )
      {
        v10 = v25;
        do
          v10 = v10->parent;
        while ( v10 );
      }
      goto LABEL_28;
    }
    v25 = v1->parent;
    v26 = v1->red;
  }
  else
  {
    child_left = v1->child_right;
    v25 = v1->parent;
    v26 = v1->red;
    if ( !child_left )
      goto LABEL_64;
  }
  child_left->parent = v25;
LABEL_64:
  if ( v25 )
  {
    if ( v25->child_left == v1 )
      v25->child_left = child_left;
    else
      v25->child_right = child_left;
  }
  else
  {
    g_Rows_Head = child_left;
  }
LABEL_28:
  if ( v26 )
    goto LABEL_29;
  v11 = g_Rows_Head;
  while ( 1 )
  {
    if ( child_left && child_left->red )
    {
      g_Rows_Head = v11;
      goto LABEL_69;
    }
    if ( child_left == v11 )
    {
      g_Rows_Head = child_left;
      goto LABEL_68;
    }
    v15 = v25->child_left;
    if ( v15 != child_left )
    {
      if ( v15->red == 1 )
      {
        v16 = v15->child_right;
        v15->red = 0;
        v25->red = 1;
        v25->child_left = v16;
        if ( v16 )
          v16->parent = v25;
        v17 = v25->parent;
        v15->parent = v17;
        if ( v17 )
        {
          v18 = v25->parent;
          if ( v25 == v18->child_left )
          {
            v18->child_left = v15;
            v16 = v25->child_left;
          }
          else
          {
            v18->child_right = v15;
          }
        }
        else
        {
          v11 = v15;
        }
        v15->child_right = v25;
        v25->parent = v15;
        v15 = v16;
      }
      v12 = v15->child_left;
      if ( v12 && v12->red )
      {
        g_Rows_Head = v11;
      }
      else
      {
        v13 = v15->child_right;
        if ( !v13 || !v13->red )
        {
          v15->red = 1;
          v14 = v25->parent;
          goto LABEL_36;
        }
        g_Rows_Head = v11;
        if ( !v12 || !v12->red )
        {
          v30 = v13->child_left;
          v13->red = 0;
          v15->red = 1;
          v15->child_right = v30;
          if ( v30 )
            v30->parent = v15;
          v31 = v15->parent;
          v13->parent = v31;
          if ( v31 )
          {
            v32 = v15->parent;
            if ( v32->child_left == v15 )
              v32->child_left = v13;
            else
              v32->child_right = v13;
          }
          else
          {
            g_Rows_Head = v13;
          }
          v13->child_left = v15;
          v15->parent = v13;
          v15 = v25->child_left;
          v12 = v15->child_left;
          v15->red = v25->red;
          v25->red = 0;
          if ( !v12 )
            goto LABEL_79;
          goto LABEL_78;
        }
      }
      v15->red = v25->red;
      v25->red = 0;
LABEL_78:
      v12->red = 0;
LABEL_79:
      v27 = v15->child_right;
      v25->child_left = v27;
      if ( v27 )
        v27->parent = v25;
      v28 = v25->parent;
      v15->parent = v28;
      if ( v28 )
      {
        v29 = v25->parent;
        if ( v25 == v29->child_left )
        {
          v29->child_left = v15;
          child_left = g_Rows_Head;
        }
        else
        {
          v29->child_right = v15;
          child_left = g_Rows_Head;
        }
      }
      else
      {
        g_Rows_Head = v15;
        child_left = v15;
      }
      v15->child_right = v25;
      v25->parent = v15;
      goto LABEL_68;
    }
    v19 = v25->child_right;
    if ( v19->red == 1 )
    {
      v22 = v19->child_left;
      v19->red = 0;
      v25->red = 1;
      v25->child_right = v22;
      if ( v22 )
        v22->parent = v25;
      v23 = v25->parent;
      v19->parent = v23;
      if ( v23 )
      {
        v24 = v25->parent;
        if ( v25 == v24->child_left )
        {
          v24->child_left = v19;
        }
        else
        {
          v24->child_right = v19;
          v22 = v25->child_right;
        }
      }
      else
      {
        v11 = v19;
      }
      v19->child_left = v25;
      v25->parent = v19;
      v19 = v22;
    }
    v20 = v19->child_left;
    if ( v20 )
    {
      if ( v20->red )
        break;
    }
    v21 = v19->child_right;
    if ( v21 && v21->red )
    {
      g_Rows_Head = v11;
LABEL_117:
      v36 = v25->child_right;
      v19->red = v25->red;
      v25->red = 0;
      goto LABEL_108;
    }
    v19->red = 1;
    v14 = v25->parent;
LABEL_36:
    child_left = v25;
    v25 = v14;
  }
  v21 = v19->child_right;
  g_Rows_Head = v11;
  if ( v21 && v21->red )
    goto LABEL_117;
  v33 = v20->child_right;
  v20->red = 0;
  v19->red = 1;
  v19->child_left = v33;
  if ( v33 )
    v33->parent = v19;
  v34 = v19->parent;
  v20->parent = v34;
  if ( v34 )
  {
    v35 = v19->parent;
    if ( v19 == v35->child_left )
      v35->child_left = v20;
    else
      v35->child_right = v20;
  }
  else
  {
    g_Rows_Head = v20;
  }
  v20->child_right = v19;
  v19->parent = v20;
  v36 = v25->child_right;
  v21 = v36->child_right;
  v36->red = v25->red;
  v25->red = 0;
  if ( v21 )
LABEL_108:
    v21->red = 0;
  v37 = v36->child_left;
  v25->child_right = v37;
  if ( v37 )
    v37->parent = v25;
  v38 = v25->parent;
  v36->parent = v38;
  if ( v38 )
  {
    v39 = v25->parent;
    if ( v25 == v39->child_left )
    {
      v39->child_left = v36;
      child_left = g_Rows_Head;
    }
    else
    {
      v39->child_right = v36;
      child_left = g_Rows_Head;
    }
  }
  else
  {
    g_Rows_Head = v36;
    child_left = v36;
  }
  v36->child_left = v25;
  v25->parent = v36;
LABEL_68:
  if ( !child_left )
    goto LABEL_29;
LABEL_69:
  child_left->red = 0;
LABEL_29:
  free((void *)v2);
  free(v1->data);
  free(v1);
  free(v0);
  return puts("INFO: Delete successful.");
}

//----- (0000000000001A20) ----------------------------------------------------
uint64_t rep()
{
  uint8_t v0; // zf@1
  uint64_t v1; // rdi@1
  int64_t v2; // rcx@1
  char *v3; // rsi@1
  uint64_t v4; // rdi@5
  int64_t v5; // rcx@5
  char *v6; // rsi@5
  uint64_t v7; // rdi@9
  int64_t v8; // rcx@9
  char *v9; // rsi@9
  uint64_t v10; // rdi@13
  int64_t v11; // rcx@13
  char *v12; // rsi@13
  uint64_t v13; // rdi@17
  int64_t v14; // rcx@17
  char *v15; // rsi@17
  char command[8]; // [sp+0h] [bp-18h]@1
  uint64_t cookie; // [sp+8h] [bp-10h]@1

  puts("PROMPT: Enter command:");
  stdin_get(command, 8LL);
  v1 = (uint64_t)"GET\n";
  v2 = 5LL;
  v3 = command;
  do
  {
    if ( !v2 )
      break;
    v0 = *v3++ == *(uint8_t *)v1++;
    --v2;
  }
  while ( v0 );
  if ( v0 )
  {
    command_get();
  }
  else
  {
    v4 = (uint64_t)"PUT\n";
    v5 = 5LL;
    v6 = command;
    do
    {
      if ( !v5 )
        break;
      v0 = *v6++ == *(uint8_t *)v4++;
      --v5;
    }
    while ( v0 );
    if ( v0 )
    {
      command_put();
    }
    else
    {
      v7 = (uint64_t)"DUMP\n";
      v8 = 6LL;
      v9 = command;
      do
      {
        if ( !v8 )
          break;
        v0 = *v9++ == *(uint8_t *)v7++;
        --v8;
      }
      while ( v0 );
      if ( v0 )
      {
        command_dump();
      }
      else
      {
        v10 = (uint64_t)"DEL\n";
        v11 = 5LL;
        v12 = command;
        do
        {
          if ( !v11 )
            break;
          v0 = *v12++ == *(uint8_t *)v10++;
          --v11;
        }
        while ( v0 );
        if ( v0 )
        {
          command_del();
        }
        else
        {
          v13 = (uint64_t)"EXIT\n";
          v14 = 6LL;
          v15 = command;
          do
          {
            if ( !v14 )
              break;
            v0 = *v15++ == *(uint8_t *)v13++;
            --v14;
          }
          while ( v0 );
          if ( v0 )
            fuckitall();
          printf("ERROR: '%s' is not a valid command.\n", command);
        }
      }
    }
  }
  return 0;
}

