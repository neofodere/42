/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parsing.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

void	print_usage_error(void)
{
	fprintf(stderr, "Error: invalid arguments.\n");
	fprintf(stderr, "Usage: ./codexion number_of_coders time_to_burnout ");
	fprintf(stderr, "time_to_compile time_to_debug time_to_refactor ");
	fprintf(stderr, "number_of_compiles_required dongle_cooldown scheduler\n");
	fprintf(stderr, "scheduler must be exactly: fifo or edf\n");
}

static int	parse_scheduler(const char *s, t_scheduler *out)
{
	if (strcmp(s, POLICY_FIFO_STR) == 0)
	{
		*out = POLICY_FIFO;
		return (1);
	}
	if (strcmp(s, POLICY_EDF_STR) == 0)
	{
		*out = POLICY_EDF;
		return (1);
	}
	return (0);
}

int	parse_arguments(t_data *data, char **argv)
{
	long long	tmp;

	if (!parse_positive(argv[1], &tmp) || tmp < 1)
		return (0);
	data->number_of_coders = (int)tmp;
	if (!parse_positive(argv[2], &data->time_to_burnout))
		return (0);
	if (!parse_positive(argv[3], &data->time_to_compile))
		return (0);
	if (!parse_positive(argv[4], &data->time_to_debug))
		return (0);
	if (!parse_positive(argv[5], &data->time_to_refactor))
		return (0);
	if (!parse_positive(argv[6], &tmp))
		return (0);
	data->number_of_compiles_required = (int)tmp;
	if (!parse_positive(argv[7], &data->dongle_cooldown))
		return (0);
	if (!parse_scheduler(argv[8], &data->scheduler))
		return (0);
	return (1);
}
