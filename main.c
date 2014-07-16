#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>
#include <unistd.h>

#include <ncurses.h>

#define WIDTH 100
#define HEIGHT 40
#define FPS 25

// The bottom of a pipe must take up this many chars
#define MIN_PIPE_BOTTOM 5
// The top of a pipe must take up this many chars
#define MIN_PIPE_TOP 5
// There must be this many chars of space for the player to move through
#define PIPE_GAP 10
#define PIPE_CHAR 'H'
#define PIPE_SPACE 25
#define INITIAL_SPACE 50
#define PLAYER_CHAR 'P'
#define GRAVITY_ACCEL 0.15
#define PLAYER_START_VELOCITY 0
#define PLAYER_JUMP_VELOCITY -1.5
#define PIPE_WIDTH 5

static struct {
    char world[WIDTH][HEIGHT];
    float playerY;
    float playerYVelocity;
} gameData;

static int init();
static void draw();
static void draw_border();
static void draw_end();
static void update();
static void player_jump();
static int sync_loop();
static int get_top_length(int height);
static void make_pipe(char* const col, int length, int top_length);
static void check_window_size();

static WINDOW* screen;
static int score = 0;

int main() {
    int return_val = 0;
    if (init() == -1) {
        return_val = -1;
        goto main_end;
    }

	char in;

	draw();
	in  = getch();
	while (in != ' ') {
		in = getch();
	}
	player_jump();

    while (true) {
        in = getch();
        if (in == 'q') {
            break;
        } else if (in == ' '){
            player_jump();
        }

        update();
        draw();
        if (sync_loop() == -1) {
            return_val = -2;
            goto main_end;
        }
        if (gameData.world[0][(int)gameData.playerY] == PIPE_CHAR ||
                gameData.playerY > HEIGHT || gameData.playerY < 0) {
            break;
        }
    }
    draw_end();
    nodelay(screen, false);
    getch();
main_end:
    endwin();
    return return_val;
}

static void update() {
    static int pipe_count = PIPE_SPACE + INITIAL_SPACE;
    static int top_length = 0;
    score++;
    for (int i = 1; i < WIDTH; i++) {
        memcpy(gameData.world[i - 1], gameData.world[i], HEIGHT * sizeof(char));
    }
    pipe_count--;
    if (pipe_count <= 0) {
        if (top_length == 0) {
            top_length = get_top_length(HEIGHT);
        }
        make_pipe(gameData.world[WIDTH - 1], HEIGHT, top_length);
        // use pipe_count as both the counter between pipe starts and the
        // counter for the width of each pipe
        if (pipe_count <= 1 - PIPE_WIDTH) {
            pipe_count = PIPE_SPACE;
            top_length = 0;
        }
    } else {
        memset(gameData.world[WIDTH - 1], ' ', HEIGHT * sizeof(char));
    }
    gameData.playerY += gameData.playerYVelocity;
    gameData.playerYVelocity += GRAVITY_ACCEL;
}

static void player_jump() {
    gameData.playerYVelocity = PLAYER_JUMP_VELOCITY;
}

static void draw() {
    check_window_size();
    draw_border();
    for (int i = 0; i < HEIGHT; i++) {
        move(i + 1, 1);
        for (int j = 0; j < WIDTH; j++) {
            addch(gameData.world[j][i]);
        }
    }
    move(((int)gameData.playerY) + 1, 1);
    addch(PLAYER_CHAR);
    move(HEIGHT, WIDTH - 12);
    printw("Score: %d", score);
    refresh();
}

static void draw_border() {
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

static void draw_end() {
    erase();
    move(0,0);
    printw("Game Over! Final Score: %d (Press any key to quit)", score);
}

static int sync_loop() {
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

static int init() {
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
    for (int i = 0; i < WIDTH; i++) {
        memset(gameData.world[i], ' ', HEIGHT * sizeof(char));
    }
    gameData.playerY = HEIGHT / 2;
    gameData.playerYVelocity = PLAYER_START_VELOCITY;
    return 0;
init_err:
    return -1;
}

static int get_top_length(int height) {
    int max_top_extra_len = height - MIN_PIPE_TOP - MIN_PIPE_BOTTOM -
        PIPE_GAP;
    return rand() % max_top_extra_len;
}

static void make_pipe(char* const col, int height, int top_length) {
    int top_count = MIN_PIPE_TOP + top_length;
    int space_count = PIPE_GAP;
    for (int i = 0; i < height; i++) {
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

static void check_window_size() {
    while (true) {
        int width = getmaxx(screen);
        int height = getmaxy(screen);
        if (width < WIDTH + 2 || height < HEIGHT + 2) {
            erase();
            move(0, 0);
            // HEIGHT + 4 because ncurses needs 2 extra chars on the bottom
            printw("Increase terminal width to %d by %d to continue", WIDTH + 2, HEIGHT + 4);
            refresh();
            sleep(1);
        } else {
            break;
        }
    }
}
