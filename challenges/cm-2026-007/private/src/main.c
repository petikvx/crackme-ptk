#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Encoded password bytes (XOR with a fixed key). Seed=153 */
static const unsigned char enc[] = { 0x7a, 0x59, 0x5f, 0x4d, 0x68, 0x0e, 0x7d, 0x09, 0x70, 0x77, 0x65, 0x71, 0 };
static const unsigned char xor_key = 0x3c;

static int check(const char *input) {
    size_t n = sizeof(enc) - 1;
    char *buf;
    size_t i;
    int ok;

    if (strlen(input) != n) {
        return 0;
    }

    buf = (char *)malloc(n + 1);
    if (!buf) {
        return 0;
    }

    for (i = 0; i < n; i++) {
        buf[i] = (char)(enc[i] ^ xor_key);
    }
    buf[n] = '\0';

    ok = (strcmp(input, buf) == 0);
    /* Best-effort wipe */
    memset(buf, 0, n);
    free(buf);
    return ok;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <password>\n", argv[0]);
        return 1;
    }

    if (check(argv[1])) {
        puts("Access granted!");
        return 0;
    }

    puts("Access denied.");
    return 1;
}
