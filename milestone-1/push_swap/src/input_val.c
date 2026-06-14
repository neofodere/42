/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   input_val.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	check_args(char **args, int argc)
{
	int	index;

	index = 0;
	while (index < argc - 1)
	{
		if (check_num(args[index + 1]) == -1 || *args[index + 1] == '\0')
			return (-1);
		index++;
	}
	return (0);
}

int	check_num(char *str)
{
	int	count;
	int	pos;

	count = 0;
	pos = 0;
	if (((str[pos] == '-' || str[pos] == '+')
			&& (str[pos + 1] >= '0' && str[pos + 1] <= '9'))
		|| (str[pos] >= '0' && str[pos] <= '9'))
	{
		count++;
		pos++;
		while (str[pos])
		{
			if (str[pos] >= '0' && str[pos] <= '9')
				count++;
			pos++;
		}
	}
	if (count == ft_strlen(str))
		return (0);
	return (-1);
}

int	check_order(t_list *data)
{
	int	pos;
	int	count;

	pos = 0;
	count = 0;
	while (pos < data->argc - 1)
	{
		if (data->sa[pos] < data->sa[pos + 1])
			count++;
		pos++;
	}
	if (count == pos)
		return (-1);
	return (0);
}

static int	check_duplicate_limit(t_list *data, int num, int pos)
{
	int	index;

	index = 0;
	while (index < pos)
	{
		if (data->sa[index] == num)
			return (0);
		index++;
	}
	return (1);
}

int	check_duplicates(t_list *data)
{
	int	pos;

	pos = 0;
	while (pos < data->sia)
	{
		if (check_duplicate_limit(data, data->sa[pos], pos) == 0)
			return (-1);
		pos++;
	}
	return (0);
}
