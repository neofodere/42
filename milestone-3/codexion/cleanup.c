/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   cleanup.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
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
