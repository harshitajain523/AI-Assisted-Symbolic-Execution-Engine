int validate_input(int len, int choice) {
    char buffer[MAX_LEN];
    if (len < 0 || len > 64) {
        return -1;                       // Reject obviously bad lengths
    }

    // Safe early exit path
    if (choice == 42) {
        return 42;
    }

    // Fix: Ensure memcpy does not exceed buffer bounds (MAX_LEN=32)
    klee_make_symbolic(buffer, sizeof(buffer), "buffer");
    char payload[64];
    klee_make_symbolic(payload, sizeof(payload), "payload");
    
    size_t copy_len = (size_t)len;
    if (copy_len > MAX_LEN) {
        copy_len = MAX_LEN;
    }
    
    memcpy(buffer, payload, copy_len);

    // Additional branching logic
    if (buffer[0] == 'A' && buffer[1] == 'Z') {
        return len * 2;
    }
    return len + choice;
}