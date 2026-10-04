/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   libft.h                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/10/08 13:31:41 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef LIBFT_H
# define LIBFT_H
# include <stddef.h>
# include <stdlib.h>
# include <unistd.h>

void	*ft_memset(void *mem_block, int value, size_t byte_quant);
void	ft_bzero(void *mem_block, size_t byte_quant);
void	*ft_memcpy(void *dest_block, const void *src_block, size_t byte_quant);
void	*ft_memmove(void *dest_block, const void *src_block, size_t byte_quant);
void	ft_striteri(char *s, void (*f)(unsigned int, char*));
void	ft_putchar_fd(char c, int fd);
void	ft_putstr_fd(char *s, int fd);
void	ft_putendl_fd(char *s, int fd);
void	ft_putnbr_fd(int n, int fd);
void	*ft_calloc(size_t elmnt_count, size_t elmnt_size);
void	*ft_memchr(const void *mem_block, int trgt_byte, size_t byte_quant);
char	*ft_strdup(const char *src_str);
char	*ft_strchr(const char *str, int trgt_c);
char	*ft_strrchr(const char *str, int c);
char	*ft_strnstr(const char *str, const char *word, size_t len);
char	*ft_substr(char const *s, unsigned int start, size_t len);
char	*ft_strjoin(char const *s1, char const *s2);
char	*ft_strtrim(char const *s1, char const *set);
char	**ft_split(char const *s, char c);
char	*ft_itoa(int n);
char	*ft_strmapi(char const *s, char (*f)(unsigned int, char));
char	*ft_utoa(unsigned int nbr);
size_t	ft_strlcpy(char *dest_str, const char *src_str, size_t dest_size);
size_t	ft_strlcat(char *dest_str, const char *src_str, size_t dest_size);
size_t	ft_strlen(const char *str);
int		ft_isalpha(int c);
int		ft_isdigit(int c);
int		ft_isalnum(int c);
int		ft_isascii(int c);
int		ft_isprint(int c);
int		ft_toupper(int c);
int		ft_tolower(int c);
int		ft_strncmp(const char *str1, const char *str2, size_t limit);
int		ft_memcmp(const void *block_a, const void *block_b, size_t byte_quant);
int		ft_atoi(const char *str);

#endif
