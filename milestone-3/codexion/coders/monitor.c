/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   monitor.c                                            :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */
#include "codexion.h"

static int	find_burned_out(t_data *data)
{
	int			i;
	long long	now;
	long long	deadline;

	i = 0;
	while (i < data->number_of_coders)
	{
		pthread_mutex_lock(&data->compile_mutex);
		now = elapsed_ms(data);
		deadline = data->coders[i].last_compile_start + data->time_to_burnout;
		pthread_mutex_unlock(&data->compile_mutex);
		if (now > deadline)
			return (i);
		i++;
	}
	return (-1);
}

static void	announce_burnout(t_data *data, int idx)
{
	long long	t;

	pthread_mutex_lock(&data->state_mutex);
	if (!data->stop)
	{
		t = elapsed_ms(data);
		printf("%lld %d burned out\n", t, data->coders[idx].id);
		data->stop = 1;
	}
	pthread_mutex_unlock(&data->state_mutex);
	pthread_mutex_lock(&data->sched_mutex);
	pthread_cond_broadcast(&data->sched_cond);
	pthread_mutex_unlock(&data->sched_mutex);
}

void	*monitor_routine(void *arg)
{
	t_data	*data;
	int		burned;

	data = (t_data *)arg;
	while (!simulation_stopped(data))
	{
		burned = find_burned_out(data);
		if (burned != -1)
		{
			announce_burnout(data, burned);
			break ;
		}
		usleep(POLL_STEP_US);
	}
	return (NULL);
}
