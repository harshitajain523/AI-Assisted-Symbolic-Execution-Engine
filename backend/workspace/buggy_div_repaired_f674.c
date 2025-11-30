#include <klee/klee.h>
#include <string.h>

int check(char *s) {
    if (strlen(s) > 5)
        return -1;

    if (s[0] == 'A') {
        if (s[1] == 'B')
            return 1;
    }

    return 0;
}

int main() {
    char buf[4];
    // Make only N-1 bytes symbolic to reserve space for the null terminator.
    klee_make_symbolic(buf, sizeof(buf) - 1, "buf");
    // Explicitly null terminate the buffer to prevent strlen over-read.
    buf[sizeof(buf) - 1] = '\0';
    return check(buf);
}