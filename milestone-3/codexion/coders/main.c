/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   main.c                                               :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */
#include "codexion.h"

int	main(int argc, char **argv)
{
	t_data	data;

	if (argc != 9)
	{
		print_usage_error();
		return (1);
	}
	if (!parse_arguments(&data, argv))
	{
		print_usage_error();
		return (1);
	}
	if (!init_data(&data))
		return (1);
	if (!run_simulation(&data))
	{
		cleanup_data(&data);
		return (1);
	}
	cleanup_data(&data);
	return (0);
}
