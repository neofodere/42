/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strncmp.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_strncmp(const char *str1, const char *str2, size_t limit)
{
	size_t	pos;

	pos = 0;
	while (pos < limit && (str1[pos] || str2[pos]))
	{
		if ((unsigned char)str1[pos] != (unsigned char)str2[pos])
			return ((unsigned char)str1[pos] - (unsigned char)str2[pos]);
		pos++;
	}
	return (0);
}
