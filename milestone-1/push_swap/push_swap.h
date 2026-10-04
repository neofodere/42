/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_SWAP_H
# define PUSH_SWAP_H

# include <unistd.h>
# include <stdlib.h>
# include <limits.h>

typedef struct s_list
{
	int	*sa;
	int	*sb;
	int	*sp;
	int	argc;
	int	sia;
	int	sib;
	int	sip;
	int	lsp;
	int	argmax;
	int	control;
	int	percentage;
	int	cont;
	int	size_block;
	int	error;
	int	atoierror;
}	t_list;

void	free_data(t_list *data);
void	free_data_safe(t_list *data);
void	sa(t_list *data);
void	sb(t_list *data);
void	pa(t_list *data);
void	pb(t_list *data);
void	swap(int *a, int *b);
void	ra(t_list *data);
void	rb(t_list *data);
void	rr(t_list *data);
void	rra(t_list *data);
void	rrb(t_list *data);
void	rrr(t_list *data);
void	sort_3(int *a, t_list *data);
void	sort_4(int *a, t_list *data);
void	sort_5(int *a, t_list *data);
void	sort_100(t_list *data);
void	sort_500(t_list *data);
void	sort_numbers(t_list *data);
void	normalize_numbers(t_list *data);
void	order_numbers(t_list *data);
void	order_sb(t_list *data);
void	order_sb_rotate(t_list *data);
void	order_numbers_aux(t_list *data);
char	*ft_substr(char *str, int pos, int len);
int		init_data(t_list *data);
int		args_to_int(t_list *data, int argc, char **args);
int		choose_algoritm(int argc, t_list *data);
int		check_args(char **args, int argc);
int		check_num(char *str);
int		check_order(t_list *data);
int		check_duplicates(t_list *data);
int		error_exit(t_list *data, int num);
int		ft_atoi(const char *str, t_list *data);
int		ft_isdigit(int c);
int		ft_strlen(char *str);

#endif
