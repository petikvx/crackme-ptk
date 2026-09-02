#include <ctype.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define SEED 0x12345678u

static void make_serial(const char *username, char out[20]) {
    uint32_t state = (SEED ^ 0x9E3779B9u);
    const unsigned char *p = (const unsigned char *)username;
    int i;

    while (*p) {
        state = state * 1664525u + (uint32_t)(*p) + 1013904223u;
        state ^= state << 13;
        state ^= state >> 17;
        state ^= state << 5;
        p++;
    }

    for (i = 0; i < 4; i++) {
        state = state * 1664525u + 1013904223u;
        if (i) {
            out[i * 5 - 1] = '-';
        }
        sprintf(out + i * 5, "%04X", (unsigned)(state & 0xFFFFu));
    }
}

static int norm_eq(const char *a, const char *b) {
    while (*a && *b) {
        if (toupper((unsigned char)*a) != toupper((unsigned char)*b)) {
            return 0;
        }
        a++;
        b++;
    }
    return *a == '\0' && *b == '\0';
}

int main(int argc, char **argv) {
    char expect[20];

    if (argc != 3) {
        fprintf(stderr, "Usage: %s <username> <serial>\n", argv[0]);
        return 1;
    }

    if (argv[1][0] == '\0') {
        puts("Invalid username.");
        return 1;
    }

    make_serial(argv[1], expect);

    if (norm_eq(argv[2], expect)) {
        puts("License valid!");
        return 0;
    }

    puts("Invalid license.");
    return 1;
}
