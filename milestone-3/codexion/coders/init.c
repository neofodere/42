/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   init.c                                               :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	alloc_arrays(t_data *data)
{
	data->dongles = malloc(sizeof(t_dongle) * (size_t)data->number_of_coders);
	data->coders = malloc(sizeof(t_coder) * (size_t)data->number_of_coders);
	heap_init(&data->heap, data->number_of_coders);
	if (!data->dongles || !data->coders || !data->heap.nodes)
		return (0);
	return (1);
}

static void	init_dongles(t_data *data)
{
	int	i;

	i = 0;
	while (i < data->number_of_coders)
	{
		data->dongles[i].busy = 0;
		data->dongles[i].cooldown_until = 0;
		i++;
	}
}

static void	init_coders(t_data *data)
{
	int	i;
	int	n;

	n = data->number_of_coders;
	i = 0;
	while (i < n)
	{
		data->coders[i].id = i + 1;
		data->coders[i].left = i;
		data->coders[i].right = (i + 1) % n;
		data->coders[i].compiles_done = 0;
		data->coders[i].last_compile_start = 0;
		data->coders[i].data = data;
		i++;
	}
}

static void	init_sync(t_data *data)
{
	data->seq_counter = 0;
	data->stop = 0;
	pthread_mutex_init(&data->sched_mutex, NULL);
	pthread_cond_init(&data->sched_cond, NULL);
	pthread_mutex_init(&data->state_mutex, NULL);
	pthread_mutex_init(&data->compile_mutex, NULL);
}

int	init_data(t_data *data)
{
	if (!alloc_arrays(data))
	{
		fprintf(stderr, "Error: allocation failed.\n");
		return (0);
	}
	init_dongles(data);
	init_coders(data);
	init_sync(data);
	data->start_time = get_time_ms();
	return (1);
}
