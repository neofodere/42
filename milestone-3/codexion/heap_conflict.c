/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   heap_conflict.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	requests_conflict(t_request a, t_request b)
{
	if (a.left == b.left || a.left == b.right)
		return (1);
	if (a.right == b.left || a.right == b.right)
		return (1);
	return (0);
}

int	heap_has_smaller_conflict(t_heap *h, t_request req)
{
	int	i;

	i = 0;
	while (i < h->size)
	{
		if (h->nodes[i].coder_id != req.coder_id
			&& requests_conflict(h->nodes[i], req)
			&& h->nodes[i].key < req.key)
			return (1);
		i++;
	}
	return (0);
}
