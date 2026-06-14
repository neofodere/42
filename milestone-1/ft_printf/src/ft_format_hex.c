/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_format_hex.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"
#include "libft/libft.h"

static int	print_hex_aux(unsigned long nbr, int upper)
{
	char	*hex;
	int		count;

	count = 0;
	if (!upper)
		hex = "0123456789abcdef";
	else
		hex = "0123456789ABCDEF";
	if (nbr >= 16)
		count += print_hex(nbr / 16, upper);
	write(1, &hex[nbr % 16], 1);
	return (count + 1);
}

int	print_hex(unsigned int nbr, int upper)
{
	return (print_hex_aux(nbr, upper));
}
