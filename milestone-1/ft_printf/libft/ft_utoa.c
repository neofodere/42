/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_utoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	count_digits(unsigned int nbr)
{
	int	pos;

	pos = 1;
	while (nbr >= 10)
	{
		nbr /= 10;
		pos++;
	}
	return (pos);
}

char	*ft_utoa(unsigned int nbr)
{
	char	*str;
	int		len;

	len = count_digits(nbr);
	str = malloc(len + 1);
	if (!str)
		return (NULL);
	str[len] = '\0';
	while (len--)
	{
		str[len] = '0' + (nbr % 10);
		nbr /= 10;
	}
	return (str);
}
