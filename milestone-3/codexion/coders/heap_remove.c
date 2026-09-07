/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   heap_remove.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	heap_sift_down(t_heap *h, int i)
{
	int	left;
	int	right;
	int	smallest;

	while (1)
	{
		left = i * 2 + 1;
		right = i * 2 + 2;
		smallest = i;
		if (left < h->size && h->nodes[left].key < h->nodes[smallest].key)
			smallest = left;
		if (right < h->size && h->nodes[right].key < h->nodes[smallest].key)
			smallest = right;
		if (smallest == i)
			break ;
		heap_swap(&h->nodes[i], &h->nodes[smallest]);
		i = smallest;
	}
}

static int	heap_find_index(t_heap *h, int coder_id)
{
	int	i;

	i = 0;
	while (i < h->size)
	{
		if (h->nodes[i].coder_id == coder_id)
			return (i);
		i++;
	}
	return (-1);
}

void	heap_remove(t_heap *h, int coder_id)
{
	int	idx;

	idx = heap_find_index(h, coder_id);
	if (idx == -1)
		return ;
	h->size--;
	h->nodes[idx] = h->nodes[h->size];
	if (idx < h->size)
	{
		heap_sift_down(h, idx);
		heap_sift_up(h, idx);
	}
}
