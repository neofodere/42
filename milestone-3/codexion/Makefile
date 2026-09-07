NAME	= codexion

CC	= cc
CFLAGS	= -Wall -Wextra -Werror -pthread

SRCS	= coders/main.c \
          coders/parsing.c \
          coders/parsing_utils.c \
          coders/init.c \
          coders/simulation.c \
          coders/cleanup.c \
          coders/utils.c \
          coders/sync_utils.c \
          coders/heap.c \
          coders/heap_remove.c \
          coders/heap_conflict.c \
          coders/dongle.c \
          coders/dongle_release.c \
          coders/coder.c \
          coders/monitor.c

OBJS	= $(SRCS:.c=.o)
HEADER	= coders/codexion.h

all: $(NAME)

$(NAME): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(NAME)

%.o: %.c $(HEADER)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
