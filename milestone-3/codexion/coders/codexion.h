/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   codexion.h                                           :+:      :+:    :+: */
/*                                                        +:+ +:+         +:+ */
/*   By: student <student@student.42.fr>                   +#+  +:+       +#+ */
/*                                                          +#+#+#+#+#+   +#+ */
/*   Created: 2026/01/01 00:00:00 by student                       #+#    #+# */
/*   Updated: 2026/01/01 00:00:00 by student                ###   ########.fr */
/*                                                                            */
/* ************************************************************************** */
#ifndef CODEXION_H
# define CODEXION_H

# include <pthread.h>
# include <stdio.h>
# include <stdlib.h>
# include <string.h>
# include <sys/time.h>
# include <unistd.h>

# define POLICY_FIFO_STR "fifo"
# define POLICY_EDF_STR "edf"
# define MAX_ARG_VALUE 2000000000LL
# define POLL_STEP_US 500

typedef enum e_scheduler
{
	POLICY_FIFO,
	POLICY_EDF
}	t_scheduler;

typedef struct s_dongle
{
	int				busy;
	long long		cooldown_until;
}	t_dongle;

typedef struct s_request
{
	int				coder_id;
	int				left;
	int				right;
	long long		key;
}	t_request;

typedef struct s_heap
{
	t_request		*nodes;
	int				size;
	int				capacity;
}	t_heap;

typedef struct s_data	t_data;

typedef struct s_coder
{
	int				id;
	int				left;
	int				right;
	int				compiles_done;
	long long		last_compile_start;
	pthread_t		thread;
	t_data			*data;
}	t_coder;

struct s_data
{
	int				number_of_coders;
	long long		time_to_burnout;
	long long		time_to_compile;
	long long		time_to_debug;
	long long		time_to_refactor;
	int				number_of_compiles_required;
	long long		dongle_cooldown;
	t_scheduler		scheduler;
	long long		start_time;
	long long		seq_counter;
	int				stop;
	t_dongle		*dongles;
	t_coder			*coders;
	t_heap			heap;
	pthread_t		monitor;
	pthread_mutex_t	sched_mutex;
	pthread_cond_t	sched_cond;
	pthread_mutex_t	state_mutex;
	pthread_mutex_t	compile_mutex;
};

/* parsing.c / parsing_utils.c */
int			parse_arguments(t_data *data, char **argv);
void		print_usage_error(void);
int			parse_positive(const char *s, long long *out);

/* init.c */
int			init_data(t_data *data);
int			run_simulation(t_data *data);

/* cleanup.c */
void		cleanup_data(t_data *data);

/* utils.c */
long long	get_time_ms(void);
long long	elapsed_ms(t_data *data);
int			safe_print(t_data *data, int id, const char *msg);
int			simulation_stopped(t_data *data);
void		precise_sleep(t_data *data, long long ms);
void		build_timeout(long long ms, struct timespec *ts);

/* heap.c / heap_remove.c / heap_conflict.c */
void		heap_init(t_heap *h, int capacity);
void		heap_free(t_heap *h);
void		heap_swap(t_request *a, t_request *b);
void		heap_sift_up(t_heap *h, int i);
void		heap_push(t_heap *h, t_request req);
void		heap_remove(t_heap *h, int coder_id);
int			heap_has_smaller_conflict(t_heap *h, t_request req);

/* dongle.c / dongle_release.c */
int			acquire_dongles(t_coder *coder);
void		release_dongles(t_coder *coder);
int			announce_dongles(t_coder *coder);

/* coder.c */
void		*coder_routine(void *arg);
int			register_compile_done(t_coder *coder);

/* monitor.c */
void		*monitor_routine(void *arg);

#endif
