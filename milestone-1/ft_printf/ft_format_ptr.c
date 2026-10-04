/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_format_ptr.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"
#include "libft/libft.h"

static int	print_hex_aux(unsigned long nbr)
{
	char	*hex;
	int		count;

	hex = "0123456789abcdef";
	count = 0;
	if (nbr >= 16)
		count += print_hex_aux(nbr / 16);
	write(1, &hex[nbr % 16], 1);
	return (count + 1);
}

int	print_ptr(void *ptr)
{
	unsigned long	addr;
	int				count;

	addr = (unsigned long)ptr;
	if (addr == 0)
		return (write(1, "(nil)", 5));
	write(1, "0x", 2);
	count = 2;
	count += print_hex_aux(addr);
	return (count);
}
