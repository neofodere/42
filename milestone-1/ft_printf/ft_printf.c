/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"
#include "libft/libft.h"

static int	format_intrp(int pos, int chr, char const *format, va_list args)
{
	if (format[pos] == 'c')
		chr += print_chr(va_arg(args, int));
	else if (format[pos] == 's')
		chr += print_str(va_arg(args, char *));
	else if (format[pos] == 'p')
		chr += print_ptr(va_arg(args, void *));
	else if (format[pos] == 'd' || format[pos] == 'i')
		chr += print_decimal(va_arg(args, int));
	else if (format[pos] == 'u')
		chr += print_usgn(va_arg(args, unsigned int));
	else if (format[pos] == 'x')
		chr += print_hex(va_arg(args, unsigned int), 0);
	else if (format[pos] == 'X')
		chr += print_hex(va_arg(args, unsigned int), 1);
	else if (format[pos] == '%')
		chr += print_prcn();
	return (chr);
}

int	ft_printf(char const *format, ...)
{
	va_list	args;
	int		pos;
	int		chr;

	va_start(args, format);
	pos = 0;
	chr = 0;
	while (format[pos])
	{
		if (format[pos] == '%' && format[pos + 1])
		{
			pos++;
			chr = format_intrp(pos, chr, format, args);
		}
		else
			chr += print_chr(format[pos]);
		pos++;
	}
	va_end(args);
	return (chr);
}
