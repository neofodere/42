/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memmove.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memmove(void *dest_block, const void *src_block, size_t byte_quant)
{
	unsigned char		*dest_ptr;
	const unsigned char	*src_ptr;

	dest_ptr = (unsigned char *)dest_block;
	src_ptr = (const unsigned char *)src_block;
	if (dest_ptr == src_ptr || byte_quant == 0)
		return (dest_block);
	if (dest_ptr < src_ptr)
	{
		while (byte_quant--)
			*dest_ptr++ = *src_ptr++;
	}
	else
	{
		dest_ptr += byte_quant;
		src_ptr += byte_quant;
		while (byte_quant--)
			*(--dest_ptr) = *(--src_ptr);
	}
	return (dest_block);
}
