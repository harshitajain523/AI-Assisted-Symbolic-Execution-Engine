#include <klee/klee.h>
#include <stdio.h>

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");

    if (x > 10)
        printf("Greater\n");
    else
        printf("Smaller or equal\n");

    return 0;
}