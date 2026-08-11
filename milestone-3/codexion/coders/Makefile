# ************************************************************************** #
#                                                                            #
#   Makefile                                                                #
#                                                                            #
# ************************************************************************** #

NAME		= codexion

CC			= cc
CFLAGS		= -Wall -Wextra -Werror -pthread

SRCS		= main.c \
			  parsing.c \
			  parsing_utils.c \
			  init.c \
			  simulation.c \
			  cleanup.c \
			  utils.c \
			  sync_utils.c \
			  heap.c \
			  heap_remove.c \
			  heap_conflict.c \
			  dongle.c \
			  dongle_release.c \
			  coder.c \
			  monitor.c

OBJS		= $(SRCS:.c=.o)
HEADER		= codexion.h

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
