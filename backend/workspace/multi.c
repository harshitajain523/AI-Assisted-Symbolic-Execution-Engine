#include <klee/klee.h>
int main(){int x;klee_make_symbolic(&x,sizeof(x),"x");if(x>0)return 1;else return 0;}