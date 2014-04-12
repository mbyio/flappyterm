#include <stdlib.h>
#include <stdio.h>

#include <ncurses.h>

int init();

int main() {
    if (init()) {
        return -1;
    }
    printw("Hello world !!!");
    refresh();
    getch();
    endwin();
    return 0;
}

int init() {
    if (initscr() == NULL) {
        fprintf(stderr, "initscr failed");
        goto init_err;
    }
    if (raw() == ERR) {
        fprintf(stderr, "setting raw mode failed");
        goto init_err;
    }
    if (noecho() == ERR) {
        fprintf(stderr, "setting noecho mode failed");
        goto init_err;
    }
    return 0;
init_err:
    return -1;
}
