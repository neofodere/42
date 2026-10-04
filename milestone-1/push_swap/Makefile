NAME    = push_swap
CC      ?= cc
CFLAGS  = -Wall -Werror -Wextra -fsanitize=address

ifeq (, $(shell command -v $(CC)))
	CC := /usr/bin/cc
endif

SRC =	push_swap.c \
	input_val.c \
	memory.c \
	conv.c \
	stack.c \
	rotations.c \
	rotations_aux.c \
	sort_small.c \
	sort_big.c \
	order_helpers.c

OBJ = $(SRC:.c=.o)

all: $(NAME)

$(NAME): $(OBJ) push_swap.h Makefile
	$(CC) $(CFLAGS) -o $@ $(OBJ)

%.o: %.c push_swap.h Makefile
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
