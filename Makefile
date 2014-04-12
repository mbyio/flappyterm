CC=clang
CFLAGS=-c -g -Wall -Wextra -std=gnu11 -Wfloat-equal -Wundef -Wpointer-arith \
	-Wstrict-prototypes -Wwrite-strings -Waggregate-return \
	-Wunreachable-code -Werror -Wfatal-errors
LDLIBS=-lncurses
SOURCES=main.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=flappyterm

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) $(LDLIBS) -o $@

.PHONY: clean
clean:
	rm -f main.o flappyterm
