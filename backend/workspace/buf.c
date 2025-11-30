#include <klee/klee.h>
int main(){int arr[5];int i;klee_make_symbolic(&i,sizeof(i),"i");return arr[i];}