/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   dongle_release.c                                     :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	announce_dongles(t_coder *coder)
{
	if (!safe_print(coder->data, coder->id, "has taken a dongle"))
		return (0);
	if (!safe_print(coder->data, coder->id, "has taken a dongle"))
		return (0);
	return (1);
}

void	release_dongles(t_coder *coder)
{
	t_data		*data;
	long long	now;

	data = coder->data;
	pthread_mutex_lock(&data->sched_mutex);
	now = elapsed_ms(data);
	data->dongles[coder->left].busy = 0;
	data->dongles[coder->left].cooldown_until = now + data->dongle_cooldown;
	data->dongles[coder->right].busy = 0;
	data->dongles[coder->right].cooldown_until = now + data->dongle_cooldown;
	pthread_cond_broadcast(&data->sched_cond);
	pthread_mutex_unlock(&data->sched_mutex);
}
