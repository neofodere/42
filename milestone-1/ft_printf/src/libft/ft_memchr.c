/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memchr(const void *mem_block, int trgt_byte, size_t byte_quant)
{
	unsigned char	*ptr;
	size_t			pos;

	ptr = (unsigned char *)mem_block;
	pos = 0;
	while (pos < byte_quant)
	{
		if (ptr[pos] == (unsigned char)trgt_byte)
			return ((void *)&ptr[pos]);
		pos++;
	}
	return (NULL);
}
