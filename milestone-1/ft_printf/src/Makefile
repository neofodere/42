NAME = libftprintf.a

PRINTF_SRC = ft_printf.c ft_format_chr.c ft_format_hex.c ft_format_int.c \
             ft_format_prcn.c ft_format_ptr.c ft_format_str.c ft_format_usgn_int.c

LIBFT_SRC = ft_atoi.c ft_bzero.c ft_calloc.c ft_isalnum.c ft_isalpha.c ft_isascii.c \
      ft_isdigit.c ft_isprint.c ft_memchr.c ft_memcmp.c ft_memcpy.c ft_memmove.c \
      ft_memset.c ft_putchar_fd.c ft_putendl_fd.c ft_putnbr_fd.c ft_putstr_fd.c \
      ft_split.c ft_strchr.c ft_strdup.c ft_striteri.c ft_strjoin.c ft_strlcat.c \
      ft_strlcpy.c ft_strlen.c ft_strmapi.c ft_strncmp.c ft_strnstr.c ft_strrchr.c \
      ft_strtrim.c ft_substr.c ft_tolower.c ft_toupper.c ft_itoa.c ft_utoa.c

OBJ = $(PRINTF_SRC:.c=.o)
LIBFT_OBJ = $(addprefix libft/, $(LIBFT_SRC:.c=.o))
ALL_OBJ = $(OBJ) $(LIBFT_OBJ)

CC ?= cc
CFLAGS = -Wall -Werror -Wextra

ifeq (, $(shell command -v $(CC)))
CC := /usr/bin/cc
endif

all: $(NAME)

$(NAME): $(ALL_OBJ)
	ar rcs $@ $^

%.o: %.c ft_printf.h
	$(CC) $(CFLAGS) -I libft/ -c $< -o $@

libft/%.o: libft/%.c libft/libft.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(LIBFT_OBJ)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
