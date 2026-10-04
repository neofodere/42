/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memcmp.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_memcmp(const void *block_a, const void *block_b, size_t byte_quant)
{
	unsigned char	*ptr_a;
	unsigned char	*ptr_b;
	size_t			pos;

	ptr_a = (unsigned char *)block_a;
	ptr_b = (unsigned char *)block_b;
	pos = 0;
	while (pos < byte_quant)
	{
		if (ptr_a[pos] != ptr_b[pos])
			return (ptr_a[pos] - ptr_b[pos]);
		pos++;
	}
	return (0);
}
