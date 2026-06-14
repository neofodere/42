def ft_count_harvest_recursive():
    nbr = int(input("Days until harvest: "))

    def ft_recurse(day, limit):
        if (day <= limit):
            print(f"Day {day}")
            ft_recurse(day + 1, limit)
        else:
            print("Harvest time!")

    ft_recurse(1, nbr)
