/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_big.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sort_100(t_list *data)
{
	data->lsp = data->argc - 1;
	data->control = 0;
	data->percentage = 1;
	data->cont = 4;
	data->size_block = (data->argc / data->cont) / 2;
	data->argmax = data->argc;
	sort_numbers(data);
	normalize_numbers(data);
	if (data->argc >= 20)
		order_numbers(data);
	else
		order_numbers_aux(data);
}

void	sort_500(t_list *data)
{
	data->lsp = data->argc - 1;
	data->control = 0;
	data->percentage = 1;
	data->cont = 7;
	data->size_block = (data->argc / data->cont) / 2;
	data->argmax = data->argc;
	sort_numbers(data);
	normalize_numbers(data);
	order_numbers(data);
}

void	sort_numbers(t_list *data)
{
	int	pos;
	int	count;
	int	size;

	pos = 0;
	count = 0;
	size = data->argc;
	while (count < size)
	{
		while (pos < size - 1)
		{
			if (data->sp[pos] > data->sp[pos + 1])
				swap(&data->sp[pos], &data->sp[pos + 1]);
			pos++;
		}
		pos = 0;
		count++;
	}
}

void	normalize_numbers(t_list *data)
{
	int	pos_sa;
	int	pos_sb;

	pos_sa = 0;
	pos_sb = 0;
	while (pos_sa < data->argc)
	{
		if (data->sa[pos_sa] != data->sp[pos_sb])
			pos_sb++;
		else
		{
			data->sa[pos_sa] = pos_sb;
			pos_sa++;
			pos_sb = 0;
		}
	}
}
