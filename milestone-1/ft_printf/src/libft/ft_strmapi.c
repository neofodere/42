/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strmapi.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strmapi(char const *s, char (*f)(unsigned int, char))
{
	char	*res_str;
	size_t	pos;

	if (!s || !f)
		return (NULL);
	res_str = (char *)malloc(sizeof(char) * (ft_strlen(s) + 1));
	if (!res_str)
		return (NULL);
	pos = 0;
	while (s[pos])
	{
		res_str[pos] = f(pos, s[pos]);
		pos++;
	}
	res_str[pos] = '\0';
	return (res_str);
}
