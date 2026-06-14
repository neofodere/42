/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   conv.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	ft_atoi(const char *str, t_list *data)
{
	long long	num;
	int			pos;
	int			sign;

	num = 0;
	pos = 0;
	sign = 1;
	if (str[pos] == '-' || str[pos] == '+')
	{
		if (str[pos] == '-')
			sign = -1;
		pos++;
	}
	while (str[pos] >= '0' && str[pos] <= '9')
	{
		num = num * 10 + (str[pos] - '0');
		pos++;
		if ((num > (long long)INT_MAX + 1 && sign == -1)
			|| (num > INT_MAX && sign == 1))
			return (error_exit(data, num));
	}
	return ((int)(num * sign));
}

int	ft_isdigit(int chr)
{
	return (chr >= '0' && chr <= '9');
}

int	ft_strlen(char *str)
{
	int	len;

	len = 0;
	while (str[len])
		len++;
	return (len);
}

static char	*ft_substr_aux(void)
{
	char	*copy;

	copy = malloc(1);
	if (!copy)
		return (NULL);
	copy[0] = '\0';
	return (copy);
}

char	*ft_substr(char *str, int pos, int len)
{
	char	*copy;
	int		str_len;
	int		to_copy;
	int		index;

	if (!str)
		return (NULL);
	str_len = ft_strlen(str);
	if (pos >= str_len)
		return (ft_substr_aux());
	if (len < (str_len - pos))
		to_copy = len;
	else
		to_copy = str_len - pos;
	copy = malloc(sizeof(char) * (to_copy + 1));
	if (!copy)
		return (NULL);
	index = 0;
	while (index < to_copy)
		copy[index++] = str[pos++];
	return (copy[index] = '\0', copy);
}
