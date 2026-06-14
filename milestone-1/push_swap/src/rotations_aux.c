/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rotations_aux.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

// ...[rotations.c]

static void	rrr_aux(t_list *data)
{
	int	last;
	int	pos;

	if (data->sia > 1)
	{
		last = data->sa[data->sia - 1];
		pos = data->sia - 1;
		while (pos > 0)
		{
			data->sa[pos] = data->sa[pos - 1];
			pos--;
		}
		data->sa[0] = last;
	}
}

void	rrr(t_list *data)
{
	int	last;
	int	pos;

	if ((data->sia < 2 && data->sib < 2) || !data)
		return ;
	rrr_aux(data);
	if (data->sib > 1)
	{
		last = data->sb[data->sib - 1];
		pos = data->sib - 1;
		while (pos > 0)
		{
			data->sb[pos] = data->sb[pos - 1];
			pos--;
		}
		data->sb[0] = last;
	}
	write(1, "rrr\n", 4);
}
