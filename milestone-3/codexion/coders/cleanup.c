/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   cleanup.c                                            :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */
#include "codexion.h"

void	cleanup_data(t_data *data)
{
	pthread_mutex_destroy(&data->sched_mutex);
	pthread_cond_destroy(&data->sched_cond);
	pthread_mutex_destroy(&data->state_mutex);
	pthread_mutex_destroy(&data->compile_mutex);
	heap_free(&data->heap);
	free(data->dongles);
	free(data->coders);
	data->dongles = NULL;
	data->coders = NULL;
}
