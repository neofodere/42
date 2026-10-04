/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcpy.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcpy(char *dest_str, const char *src_str, size_t dest_size)
{
	size_t	src_len;
	size_t	pos;

	src_len = 0;
	while (src_str[src_len])
		src_len++;
	if (dest_size == 0)
		return (src_len);
	pos = 0;
	while (pos < dest_size - 1 && src_str[pos])
	{
		dest_str[pos] = src_str[pos];
		pos++;
	}
	dest_str[pos] = '\0';
	return (src_len);
}
