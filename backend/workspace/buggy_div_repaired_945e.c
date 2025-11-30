#include <klee/klee.h>
#include <string.h>
#include <stdio.h>

#define MAX_LEN 32

int validate_input(int len, int choice) {
    char buffer[MAX_LEN];
    if (len < 0 || len > MAX_LEN) {
        return -1;
    }

    // Safe early exit path
    if (choice == 42) {
        return 42;
    }

    // Now safe because len is checked against MAX_LEN
    klee_make_symbolic(buffer, sizeof(buffer), "buffer");
    char payload[64];
    klee_make_symbolic(payload, sizeof(payload), "payload");
    memcpy(buffer, payload, len);

    // Additional branching logic
    if (buffer[0] == 'A' && buffer[1] == 'Z') {
        return len * 2;
    }
    return len + choice;
}

int main() {
    int len;
    int choice;
    klee_make_symbolic(&len, sizeof(len), "len");
    klee_make_symbolic(&choice, sizeof(choice), "choice");
    return validate_input(len, choice);
}