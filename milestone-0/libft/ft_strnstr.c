/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strnstr.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strnstr(const char *str, const char *word, size_t len)
{
	size_t	str_pos;
	size_t	word_pos;

	if (!*word)
		return ((char *)str);
	str_pos = 0;
	while (str[str_pos] && str_pos < len)
	{
		word_pos = 0;
		while (str[str_pos + word_pos]
			&& word[word_pos]
			&& str_pos + word_pos < len
			&& str[str_pos + word_pos] == word[word_pos])
			word_pos++;
		if (!word[word_pos])
			return ((char *)&str[str_pos]);
		str_pos++;
	}
	return (NULL);
}
