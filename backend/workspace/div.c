#include <klee/klee.h>
int main(){int x;klee_make_symbolic(&x,sizeof(x),"x");return 100/(x-10);}