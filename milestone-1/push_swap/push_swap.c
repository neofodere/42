/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	*ft_memset(void *mem_block, int value, size_t byte_quant)
{
	unsigned char	*ptr;

	ptr = (unsigned char *)mem_block;
	while (byte_quant--)
		*ptr++ = (unsigned char)value;
	return (mem_block);
}

int	init_data(t_list *data)
{
	data->sa = malloc(sizeof(int) * data->argc);
	if (!data->sa)
		return (free(data), -1);
	data->sp = malloc(sizeof(int) * data->argc);
	if (!data->sp)
		return (free(data->sa), free(data), -1);
	data->sb = malloc(sizeof(int) * data->argc);
	if (!data->sb)
		return (free(data->sp), free(data->sa), free(data), -1);
	data->sia = data->argc;
	data->sib = 0;
	data->sip = data->argc;
	return (0);
}

int	args_to_int(t_list *data, int argc, char **args)
{
	int	pos;

	pos = 0;
	while (pos < argc - 1)
	{
		if (check_num(args[pos + 1]) == -1)
			return (-1);
		data->sa[pos] = ft_atoi(args[pos + 1], data);
		if (data->atoierror == 1)
			return (-1);
		data->sp[pos] = ft_atoi(args[pos + 1], data);
		pos++;
	}
	return (0);
}

int	choose_algoritm(int argc, t_list *data)
{
	if (check_duplicates(data) == -1)
		return (-1);
	if (argc == 3 || argc == 4)
		sort_3(data->sa, data);
	else if (argc < 7 && argc > 4)
		sort_5(data->sa, data);
	else if (argc < 102 && argc > 6)
		sort_100(data);
	else if (argc > 101)
		sort_500(data);
	return (0);
}

int	main(int argc, char **argv)
{
	t_list	*data;

	if (argc <= 1)
		return (0);
	data = malloc(sizeof(t_list));
	if (!data)
		return (0);
	ft_memset(data, 0, sizeof(t_list));
	if (check_args(argv, argc - 1) == -1)
		return (free_data(data), 1);
	data->argc = argc - 1;
	data->error = 0;
	if (init_data(data) == -1)
		free_data(data);
	if (args_to_int(data, argc, argv) == -1)
		return (free_data(data), 0);
	if (check_order(data) == -1)
		free_data_safe(data);
	if (choose_algoritm(argc, data) == -1)
		free_data(data);
	free_data_safe(data);
	return (0);
}
