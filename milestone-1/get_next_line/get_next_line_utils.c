/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line_utils.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line.h"

size_t	ft_strlen(const char *str)
{
	size_t	pos;

	if (!str)
		return (0);
	pos = 0;
	while (str[pos])
		pos++;
	return (pos);
}

const char	*ft_strchr(const char *str, int chr)
{
	if (!str)
		return (NULL);
	while (*str)
	{
		if (*str == (char)chr)
			return (str);
		str++;
	}
	if ((char)chr == '\0')
		return (str);
	return (NULL);
}

static void	ft_strjoin_aux(char *dst, char *str1, const char *str2)
{
	size_t	pos1;
	size_t	pos2;

	pos1 = 0;
	pos2 = 0;
	if (str1)
	{
		while (str1 && str1[pos1])
		{
			dst[pos1] = str1[pos1];
			pos1++;
		}
	}
	while (str2[pos2])
	{
		dst[pos1] = str2[pos2];
		pos1++;
		pos2++;
	}
	dst[pos1] = '\0';
}

char	*ft_strjoin(char *str1, const char *str2)
{
	char	*join_str;
	size_t	len1;
	size_t	len2;

	if (!str1 && !str2)
		return (NULL);
	len1 = 0;
	if (str1)
		len1 = ft_strlen(str1);
	len2 = ft_strlen(str2);
	join_str = malloc(len1 + len2 + 1);
	if (!join_str)
		return (NULL);
	return (ft_strjoin_aux(join_str, str1, str2), join_str);
}
