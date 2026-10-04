/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_small.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sort_3(int *a, t_list *data)
{
	if (data->sia == 2 && a[0] > a[1])
		sa(data);
	else if (a[0] < a[1] && a[1] > a[2] && a[0] < a[2])
	{
		rra(data);
		sa(data);
	}
	else if (a[0] > a[1] && a[0] < a[2])
		sa(data);
	else if (a[0] < a[1] && a[0] > a[2])
		rra(data);
	else if (a[0] > a[1] && a[1] < a[2] && a[0] > a[2])
		ra(data);
	else if (a[0] > a[1] && a[1] > a[2])
	{
		ra(data);
		sa(data);
	}
}

void	sort_4(int *a, t_list *data)
{
	if (data->sia == 4)
	{
		if (a[0] < a[1] && a[0] < a[2] && a[0] < a[3])
			pb(data);
		else if (a[1] < a[0] && a[1] < a[2] && a[1] < a[3])
		{
			sa(data);
			pb(data);
		}
		else if (a[2] < a[0] && a[2] < a[1] && a[2] < a[3])
		{
			ra(data);
			sa(data);
			pb(data);
		}
		else
		{
			rra(data);
			pb(data);
		}
	}
	if (data->sia == 3)
		sort_3(data->sa, data);
	pa(data);
}

static int	sort_5_aux(int *a, t_list *data, int pos)
{
	if (a[2] < a[0] && a[2] < a[1] && a[2] < a[3] && a[2] < a[4] && pos == 0)
	{
		ra(data);
		sa(data);
		pb(data);
		pos++;
	}
	else if (a[3] < a[0] && a[3] < a[1] && a[3] < a[2]
		&& a[3] < a[4] && pos == 0)
	{
		rra(data);
		rra(data);
		pb(data);
		pos++;
	}
	else if (a[4] < a[0] && a[4] < a[1] && a[4] < a[2]
		&& a[4] < a[3] && pos == 0)
	{
		rra(data);
		pb(data);
		pos++;
	}
	return (pos);
}

void	sort_5(int *a, t_list *data)
{
	int	pos;

	pos = 0;
	if (data->sia == 5)
	{
		if (a[0] < a[1] && a[0] < a[2] && a[0] < a[3] && a[0] < a[4])
		{
			pb(data);
			pos++;
		}
		else if (a[1] < a[0] && a[1] < a[2] && a[1] < a[3] && a[1] < a[4])
		{
			sa(data);
			pb(data);
			pos++;
		}
		pos = sort_5_aux(a, data, pos);
	}
	sort_4(data->sa, data);
	if (pos == 1)
		pa(data);
	if (pos == 1 && a[0] > a[1])
		sa(data);
}
