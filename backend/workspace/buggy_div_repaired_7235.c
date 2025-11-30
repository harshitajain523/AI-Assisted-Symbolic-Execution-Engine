#include <klee/klee.h>
#include <stdio.h>

int vulnerable_copy(int idx) {
    int arr[5] = {1,2,3,4,5};
    if (idx < 0 || idx >= 5) {
        // Safely prevent out-of-bounds access by checking the index.
        return -1; 
    }
    return arr[idx];
}

int main() {
    int idx;
    klee_make_symbolic(&idx, sizeof(idx), "idx");

    int result = vulnerable_copy(idx);
    printf("Value = %d\n", result);
}