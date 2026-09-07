/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sync_utils.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	safe_print(t_data *data, int id, const char *msg)
{
	long long	t;

	pthread_mutex_lock(&data->state_mutex);
	if (data->stop)
	{
		pthread_mutex_unlock(&data->state_mutex);
		return (0);
	}
	t = elapsed_ms(data);
	printf("%lld %d %s\n", t, id, msg);
	pthread_mutex_unlock(&data->state_mutex);
	return (1);
}

void	build_timeout(long long ms, struct timespec *ts)
{
	struct timeval	tv;
	long long		usec;

	gettimeofday(&tv, NULL);
	usec = (long long)tv.tv_usec + ms * 1000;
	ts->tv_sec = tv.tv_sec + usec / 1000000;
	ts->tv_nsec = (usec % 1000000) * 1000;
}

void	precise_sleep(t_data *data, long long ms)
{
	long long	start;
	long long	remaining;

	start = elapsed_ms(data);
	while (!simulation_stopped(data))
	{
		remaining = ms - (elapsed_ms(data) - start);
		if (remaining <= 0)
			break ;
		if (remaining > 1)
			usleep(1000);
		else
			usleep((useconds_t)(remaining * 1000));
	}
}
