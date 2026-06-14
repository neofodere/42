/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nfodere- <>                                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/09/22 14:21:55 by nfodere-          #+#    #+#             */
/*   Updated: 2025/09/22 14:22:07 by nfodere-         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line.h"

static char	*extrct_line(char *cache)
{
	size_t	pos;
	char	*line;

	if (!cache || cache[0] == '\0')
		return (NULL);
	pos = 0;
	while (cache[pos] && cache[pos] != '\n')
		pos++;
	if (cache[pos] == '\n')
		pos++;
	line = malloc(pos + 1);
	if (!line)
		return (NULL);
	pos = 0;
	while (cache[pos] && cache[pos] != '\n')
	{
		line[pos] = cache[pos];
		pos++;
	}
	if (cache[pos] == '\n')
		line[pos++] = '\n';
	line[pos] = '\0';
	return (line);
}

static char	*updt_cache(char *cache)
{
	char		*new_cache;
	const char	*newline;

	if (!cache)
		return (NULL);
	newline = ft_strchr(cache, '\n');
	if (!newline)
		return (free(cache), NULL);
	return (new_cache = ft_strjoin(NULL, newline + 1), free(cache), new_cache);
}

static ssize_t	read_data(int fd, char **cache)
{
	char	*tmp;
	ssize_t	bytes;
	char	*joined;

	tmp = malloc(BUFFER_SIZE + 1);
	if (!tmp)
		return (-1);
	bytes = read(fd, tmp, BUFFER_SIZE);
	while (bytes > 0)
	{
		tmp[bytes] = '\0';
		joined = ft_strjoin(*cache, tmp);
		if (!joined)
			return (free(tmp), free(*cache), *cache = NULL, -1);
		free(*cache);
		*cache = joined;
		if (ft_strchr(*cache, '\n'))
			break ;
		bytes = read(fd, tmp, BUFFER_SIZE);
	}
	if (bytes == -1)
		return (free(tmp), free(*cache), *cache = NULL, -1);
	return (free(tmp), bytes);
}

char	*get_next_line(int fd)
{
	static char	*cache;
	char		*line;
	ssize_t		bytes;

	if (fd < 0 || BUFFER_SIZE <= 0)
		return (NULL);
	bytes = read_data(fd, &cache);
	if (bytes == -1)
		return (NULL);
	if (!cache || cache[0] == '\0')
		return (free(cache), cache = NULL, NULL);
	if (!ft_strchr(cache, '\n') && bytes == 0)
		return (line = extrct_line(cache), free(cache), cache = NULL, line);
	line = extrct_line(cache);
	cache = updt_cache(cache);
	return (line);
}
