/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   simulation.c                                         :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	spawn_coders(t_data *data)
{
	int	i;

	i = 0;
	while (i < data->number_of_coders)
	{
		if (pthread_create(&data->coders[i].thread, NULL,
				coder_routine, &data->coders[i]) != 0)
			return (i);
		i++;
	}
	return (i);
}

static void	join_coders(t_data *data, int count)
{
	int	i;

	i = 0;
	while (i < count)
	{
		pthread_join(data->coders[i].thread, NULL);
		i++;
	}
}

int	run_simulation(t_data *data)
{
	int	created;

	if (data->number_of_compiles_required == 0)
	{
		data->stop = 1;
		return (1);
	}
	created = spawn_coders(data);
	if (created < data->number_of_coders)
	{
		data->stop = 1;
		join_coders(data, created);
		return (0);
	}
	if (pthread_create(&data->monitor, NULL, monitor_routine, data) != 0)
	{
		data->stop = 1;
		join_coders(data, created);
		return (0);
	}
	join_coders(data, data->number_of_coders);
	pthread_join(data->monitor, NULL);
	return (1);
}
