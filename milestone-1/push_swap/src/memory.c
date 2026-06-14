/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   memory.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	free_data(t_list *data)
{
	if (data->sa)
		free(data->sa);
	if (data->sb)
		free(data->sb);
	if (data->sp)
		free(data->sp);
	if (data)
		free(data);
	write(2, "Error\n", 6);
	exit(0);
}

void	free_data_safe(t_list *data)
{
	if (data->sa)
	{
		free(data->sa);
		data->sa = NULL;
	}
	if (data->sb)
	{
		free(data->sb);
		data->sb = NULL;
	}
	if (data->sp)
	{
		free(data->sp);
		data->sp = NULL;
	}
	if (data)
	{
		free(data);
		data = NULL;
	}
	exit(0);
}

int	error_exit(t_list *data, int num)
{
	return (num = 0, data->atoierror = 1, num);
}
