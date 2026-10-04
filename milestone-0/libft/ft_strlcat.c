/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcat(char *dest_str, const char *src_str, size_t dest_size)
{
	size_t	dest_len;
	size_t	src_len;
	size_t	pos;

	dest_len = 0;
	src_len = 0;
	pos = 0;
	while (dest_str[dest_len] && dest_len < dest_size)
		dest_len++;
	while (src_str[src_len])
		src_len++;
	if (dest_len == dest_size)
		return (dest_size + src_len);
	while (src_str[pos] && (dest_len + pos + 1) < dest_size)
	{
		dest_str[dest_len + pos] = src_str[pos];
		pos++;
	}
	if (dest_len + pos < dest_size)
		dest_str[dest_len + pos] = '\0';
	return (dest_len + src_len);
}
