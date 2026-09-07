/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	can_acquire(t_coder *coder, long long key)
{
	t_data		*data;
	long long	now;
	t_request	req;

	data = coder->data;
	if (coder->left == coder->right)
		return (0);
	now = elapsed_ms(data);
	if (data->dongles[coder->left].busy)
		return (0);
	if (now < data->dongles[coder->left].cooldown_until)
		return (0);
	if (data->dongles[coder->right].busy)
		return (0);
	if (now < data->dongles[coder->right].cooldown_until)
		return (0);
	req.coder_id = coder->id;
	req.left = coder->left;
	req.right = coder->right;
	req.key = key;
	return (!heap_has_smaller_conflict(&data->heap, req));
}

static void	push_request(t_coder *coder, long long key)
{
	t_request	req;

	req.coder_id = coder->id;
	req.left = coder->left;
	req.right = coder->right;
	req.key = key;
	heap_push(&coder->data->heap, req);
}

static int	wait_for_turn(t_coder *coder, long long key)
{
	t_data			*data;
	struct timespec	ts;

	data = coder->data;
	while (!can_acquire(coder, key))
	{
		if (simulation_stopped(data))
		{
			heap_remove(&data->heap, coder->id);
			pthread_mutex_unlock(&data->sched_mutex);
			return (0);
		}
		build_timeout(1, &ts);
		pthread_cond_timedwait(&data->sched_cond, &data->sched_mutex, &ts);
	}
	return (1);
}

int	acquire_dongles(t_coder *coder)
{
	t_data		*data;
	long long	key;

	data = coder->data;
	pthread_mutex_lock(&data->sched_mutex);
	if (data->scheduler == POLICY_FIFO)
		key = data->seq_counter++;
	else
		key = coder->last_compile_start + data->time_to_burnout;
	push_request(coder, key);
	if (!wait_for_turn(coder, key))
		return (0);
	heap_remove(&data->heap, coder->id);
	data->dongles[coder->left].busy = 1;
	data->dongles[coder->right].busy = 1;
	pthread_mutex_unlock(&data->sched_mutex);
	return (announce_dongles(coder));
}
