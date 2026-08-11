/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   heap.c                                               :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

void	heap_init(t_heap *h, int capacity)
{
	h->nodes = malloc(sizeof(t_request) * (size_t)capacity);
	h->size = 0;
	h->capacity = capacity;
}

void	heap_free(t_heap *h)
{
	free(h->nodes);
	h->nodes = NULL;
	h->size = 0;
}

void	heap_swap(t_request *a, t_request *b)
{
	t_request	tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

void	heap_sift_up(t_heap *h, int i)
{
	int	parent;

	while (i > 0)
	{
		parent = (i - 1) / 2;
		if (h->nodes[parent].key <= h->nodes[i].key)
			break ;
		heap_swap(&h->nodes[parent], &h->nodes[i]);
		i = parent;
	}
}

void	heap_push(t_heap *h, t_request req)
{
	h->nodes[h->size] = req;
	h->size++;
	heap_sift_up(h, h->size - 1);
}
