/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   parsing_utils.c                                      :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	is_valid_number(const char *s)
{
	int	i;

	i = 0;
	if (!s[i])
		return (0);
	if (s[i] == '+')
		i++;
	if (!s[i])
		return (0);
	while (s[i])
	{
		if (s[i] < '0' || s[i] > '9')
			return (0);
		i++;
	}
	return (1);
}

static long long	ft_atoll(const char *s)
{
	long long	result;
	int			i;

	result = 0;
	i = 0;
	if (s[i] == '+')
		i++;
	while (s[i])
	{
		result = result * 10 + (s[i] - '0');
		if (result > MAX_ARG_VALUE)
			return (-1);
		i++;
	}
	return (result);
}

int	parse_positive(const char *s, long long *out)
{
	if (!is_valid_number(s))
		return (0);
	*out = ft_atoll(s);
	if (*out < 0)
		return (0);
	return (1);
}
