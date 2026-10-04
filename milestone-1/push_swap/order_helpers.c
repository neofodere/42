/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	order_numbers(t_list *data)
{
	int	pos;

	pos = 0;
	while (data->sia > 0)
	{
		if (data->sa[0] <= (data->percentage * data->size_block))
		{
			pb(data);
			data->control++;
			if (data->control == data->size_block)
			{
				data->percentage++;
				data->control = 0;
			}
		}
		else
			ra(data);
		pos++;
	}
	order_sb(data);
}

void	order_sb(t_list *data)
{
	while (data->sib > 0)
	{
		if (data->sb[0] == data->argmax - 1)
		{
			pa(data);
			data->argmax--;
		}
		else
			order_sb_rotate(data);
	}
}

void	order_sb_rotate(t_list *data)
{
	int	pos;

	pos = 0;
	while (data->sb[pos] != data->argmax - 1)
		pos++;
	if (pos <= data->sib / 2)
	{
		while (data->sb[0] != data->argmax - 1)
			rb(data);
	}
	else
	{
		while (data->sb[0] != data->argmax - 1)
			rrb(data);
	}
}

void	order_numbers_aux(t_list *data)
{
	while (data->sia > 0)
	{
		pb(data);
		data->control++;
		if (data->control == data->size_block)
		{
			data->percentage++;
			data->control = 0;
		}
	}
	order_sb(data);
}
