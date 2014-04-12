#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>

#include <ncurses.h>

#define WIDTH 120
#define HEIGHT 40
#define FPS 25

// The bottom of a pipe must take up this many chars
#define MIN_PIPE_BOTTOM 5
// The top of a pipe must take up this many chars
#define MIN_PIPE_TOP 5
// There must be this many chars of space for the player to move through
#define PIPE_GAP 5
#define PIPE_CHAR 'H'
#define PIPE_SPACE 20

struct {
    char world[WIDTH][HEIGHT];
} gameData;

int init();
void draw();
void draw_border();
void update();
int sync_loop();
void make_pipe(char* const col, int length);

int main() {
    if (init() == -1) {
        return -1;
    }
    do {
        update();
        draw();
        if (sync_loop() == -1) {
            return -2;
        }
    } while (getch() != 'q');
    return 0;
}

void update() {
    char old[HEIGHT];
    memcpy(old, gameData.world[0], HEIGHT * sizeof(char));
    for (int i = 1; i < WIDTH; i++) {
        memcpy(gameData.world[i - 1], gameData.world[i], HEIGHT * sizeof(char));
    }
    memcpy(gameData.world[WIDTH - 1], old, HEIGHT * sizeof(char));
}

void draw() {
    draw_border();
    for (int i = 0; i < HEIGHT; i++) {
        move(i + 1, 1);
        for (int j = 0; j < WIDTH; j++) {
            addch(gameData.world[j][i]);
        }
    }
    refresh();
}

void draw_border() {
    for (int i = 1; i <= WIDTH; i++) {
        move(0, i);
        addch('-');
        move(HEIGHT + 1, i);
        addch('-');
    }
    for (int i = 1; i <= HEIGHT; i++) {
        move(i, 0);
        addch('|');
        move(i, WIDTH + 1);
        addch('|');
    }
    move(0,0);
    addch('+');
    move(0, WIDTH + 1);
    addch('+');
    move(HEIGHT + 1,0);
    addch('+');
    move(HEIGHT + 1, WIDTH + 1);
    addch('+');
}

int sync_loop() {
    long pause = 1000000000 / FPS;
    struct timespec time = {0, pause};
    struct timespec rem = {0, 0};
    do {
        if (nanosleep(&time, &rem) == -1) {
            if (errno == EINTR) {
                time = rem;
                rem = (struct timespec){0, 0};
            } else {
                return -1;
            }
        } else {
            time = (struct timespec){0, 0};
        }
    } while (time.tv_nsec > 0);
    return 0;
}

int init() {
    WINDOW* screen;
    if ((screen = initscr()) == NULL) {
        fprintf(stderr, "initscr failed");
        goto init_err;
    }
    if (nodelay(screen, true) == ERR) {
        fprintf(stderr, "setting nodelay failed");
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
    if (curs_set(0) == ERR) {
        fprintf(stderr, "disabling the cursor failed");
        goto init_err;
    }
    int pipe_count = PIPE_SPACE;
    for (int i = 0; i < WIDTH; i++) {
        pipe_count--;
        if (pipe_count <= 0) {
            pipe_count = PIPE_SPACE;
            make_pipe(gameData.world[i], HEIGHT);
        } else {
            memset(gameData.world[i], ' ', HEIGHT * sizeof(char));
        }
    }
    return 0;
init_err:
    return -1;
}

void make_pipe(char* const col, int length) {
    int max_top_extra_len = length - MIN_PIPE_TOP - MIN_PIPE_BOTTOM -
        PIPE_GAP;
    int top_extra_len = rand() % max_top_extra_len;

    int top_count = MIN_PIPE_TOP + top_extra_len;
    int space_count = PIPE_GAP;
    for (int i = 0; i < length; i++) {
        if (top_count > 0) {
            top_count--;
            col[i] = PIPE_CHAR;
        } else if (space_count > 0) {
            space_count--;
            col[i] = ' ';
        } else {
            col[i] = PIPE_CHAR;
        }
    }
}
