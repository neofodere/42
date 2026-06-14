/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static size_t	count_words(char const *str, char sep)
{
	size_t	nbr_words;
	int		in_word;

	nbr_words = 0;
	in_word = 0;
	while (*str)
	{
		if (*str != sep && in_word == 0)
		{
			in_word = 1;
			nbr_words++;
		}
		else if (*str == sep)
			in_word = 0;
		str++;
	}
	return (nbr_words);
}

static char	*create_word(char const *str, size_t start, size_t end)
{
	char	*word;
	size_t	pos;

	word = malloc(end - start + 1);
	if (!word)
		return (NULL);
	pos = 0;
	while (start < end)
	{
		word[pos] = str[start];
		pos++;
		start++;
	}
	word[pos] = '\0';
	return (word);
}

static void	clean_words(char **words, size_t quant_words)
{
	while (quant_words > 0)
	{
		quant_words--;
		free(words[quant_words]);
	}
	free(words);
}

static char	**split(char const *str, char sep, char **words)
{
	size_t	pos;
	size_t	word_pos;
	size_t	word_start;

	pos = 0;
	word_pos = 0;
	while (str[pos])
	{
		while (str[pos] == sep)
			pos++;
		word_start = pos;
		while (str[pos] && str[pos] != sep)
			pos++;
		if (pos > word_start)
		{
			words[word_pos] = create_word(str, word_start, pos);
			if (!words[word_pos])
				return (clean_words(words, word_pos), NULL);
			word_pos++;
		}
	}
	words[word_pos] = NULL;
	return (words);
}

char	**ft_split(char const *s, char c)
{
	char	**words;
	size_t	word_quant;

	if (!s)
		return (NULL);
	word_quant = count_words(s, c);
	words = malloc(sizeof(char *) * (word_quant + 1));
	if (!words)
		return (NULL);
	return (split(s, c, words));
}
