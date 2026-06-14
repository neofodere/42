/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sa(t_list *data)
{
	int	tmp;

	if (data->sia < 2 || !data)
		return ;
	tmp = data->sa[0];
	data->sa[0] = data->sa[1];
	data->sa[1] = tmp;
	write(1, "sa\n", 3);
}

void	sb(t_list *data)
{
	int	tmp;

	if (data->sib < 2 || !data)
		return ;
	tmp = data->sb[0];
	data->sb[0] = data->sb[1];
	data->sb[1] = tmp;
	write(1, "sb\n", 3);
}

void	pa(t_list *data)
{
	int	pos;

	if (data->sib <= 0 || !data)
		return ;
	pos = data->sia;
	while (pos > 0)
	{
		data->sa[pos] = data->sa[pos - 1];
		pos--;
	}
	data->sa[0] = data->sb[0];
	pos = 0;
	while (pos < data->sib - 1)
	{
		data->sb[pos] = data->sb[pos + 1];
		pos++;
	}
	data->sib -= 1;
	data->sia += 1;
	write(1, "pa\n", 3);
}

void	pb(t_list *data)
{
	int	pos;

	if (data->sia <= 0 || !data)
		return ;
	pos = data->sib;
	while (pos > 0)
	{
		data->sb[pos] = data->sb[pos - 1];
		pos--;
	}
	data->sb[0] = data->sa[0];
	pos = 0;
	while (pos < data->sia - 1)
	{
		data->sa[pos] = data->sa[pos + 1];
		pos++;
	}
	data->sib += 1;
	data->sia -= 1;
	write(1, "pb\n", 3);
}

void	swap(int *a, int *b)
{
	int	tmp;

	if (!a || !b)
		return ;
	tmp = *a;
	*a = *b;
	*b = tmp;
}
