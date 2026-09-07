/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coder.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	signal_stop(t_data *data)
{
	pthread_mutex_lock(&data->state_mutex);
	data->stop = 1;
	pthread_mutex_unlock(&data->state_mutex);
	pthread_mutex_lock(&data->sched_mutex);
	pthread_cond_broadcast(&data->sched_cond);
	pthread_mutex_unlock(&data->sched_mutex);
}

static int	all_coders_done(t_data *data)
{
	int	i;

	i = 0;
	while (i < data->number_of_coders)
	{
		if (data->coders[i].compiles_done < data->number_of_compiles_required)
			return (0);
		i++;
	}
	return (1);
}

int	register_compile_done(t_coder *coder)
{
	t_data	*data;
	int		done;

	data = coder->data;
	pthread_mutex_lock(&data->compile_mutex);
	coder->compiles_done++;
	done = all_coders_done(data);
	pthread_mutex_unlock(&data->compile_mutex);
	if (done)
	{
		signal_stop(data);
		return (0);
	}
	return (1);
}

static int	do_compile(t_coder *coder)
{
	t_data	*data;

	data = coder->data;
	if (!acquire_dongles(coder))
		return (0);
	pthread_mutex_lock(&data->compile_mutex);
	coder->last_compile_start = elapsed_ms(data);
	pthread_mutex_unlock(&data->compile_mutex);
	if (!safe_print(data, coder->id, "is compiling"))
	{
		release_dongles(coder);
		return (0);
	}
	precise_sleep(data, data->time_to_compile);
	release_dongles(coder);
	return (register_compile_done(coder));
}

void	*coder_routine(void *arg)
{
	t_coder	*coder;
	t_data	*data;

	coder = (t_coder *)arg;
	data = coder->data;
	while (!simulation_stopped(data))
	{
		if (!do_compile(coder))
			break ;
		if (simulation_stopped(data))
			break ;
		if (!safe_print(data, coder->id, "is debugging"))
			break ;
		precise_sleep(data, data->time_to_debug);
		if (simulation_stopped(data))
			break ;
		if (!safe_print(data, coder->id, "is refactoring"))
			break ;
		precise_sleep(data, data->time_to_refactor);
	}
	return (NULL);
}
