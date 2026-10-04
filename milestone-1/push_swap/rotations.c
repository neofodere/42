/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rotations.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	ra(t_list *data)
{
	int	pos;

	if (data->sia < 2 || !data)
		return ;
	pos = 0;
	while (pos + 1 < data->sia)
	{
		swap(&data->sa[pos], &data->sa[pos + 1]);
		pos++;
	}
	write(1, "ra\n", 3);
}

void	rb(t_list *data)
{
	int	pos;

	if (data->sib < 2 || !data)
		return ;
	pos = 0;
	while (pos + 1 < data->sib)
	{
		swap(&data->sb[pos], &data->sb[pos + 1]);
		pos++;
	}
	write(1, "rb\n", 3);
}

void	rr(t_list *data)
{
	int	pos;

	if ((data->sia < 2 && data->sib < 2) || !data)
		return ;
	pos = 0;
	while (pos + 1 < data->sia)
	{
		swap(&data->sa[pos], &data->sa[pos + 1]);
		pos++;
	}
	pos = 0;
	while (pos + 1 < data->sib)
	{
		swap(&data->sb[pos], &data->sb[pos + 1]);
		pos++;
	}
	write(1, "rr\n", 3);
}

void	rra(t_list *data)
{
	int	pos;

	if (data->sia < 2 || !data)
		return ;
	pos = data->sia - 1;
	while (pos > 0)
	{
		swap(&data->sa[pos], &data->sa[pos - 1]);
		pos--;
	}
	write(1, "rra\n", 4);
}

void	rrb(t_list *data)
{
	int	pos;

	if (data->sib < 2 || !data)
		return ;
	pos = data->sib - 1;
	while (pos > 0)
	{
		swap(&data->sb[pos], &data->sb[pos - 1]);
		pos--;
	}
	write(1, "rrb\n", 4);
}

// [rotations_aux.c]...
