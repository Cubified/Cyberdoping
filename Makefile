all: detector

CC=cc

LIBS=-lm
CFLAGS=-O3 -pipe
DEBUGCFLAGS=-Og -pipe -g

INPUT=detector.c
OUTPUT=detector

RM=/bin/rm

detector: $(INPUT)
	$(CC) $(INPUT) -o $(OUTPUT) $(LIBS) $(CFLAGS)
debug: $(INPUT)
	$(CC) $(INPUT) -o $(OUTPUT) $(LIBS) $(DEBUGCFLAGS)
clean: $(OUTPUT)
	if [ -e $(OUTPUT) ]; then $(RM) $(OUTPUT); fi
