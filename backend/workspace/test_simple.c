#include <klee/klee.h>
int main(){int x; klee_make_symbolic(&x, sizeof(x), "x"); if(x > 10) return 1; return 0;}