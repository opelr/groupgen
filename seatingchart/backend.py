"""[summary]
"""

import random
from itertools import chain


def create_seating_chart(
    names: list,
    together=None,
    apart=None,
    max_size=float("Inf"),
    max_tables=float("Inf"),
    total_indiv=None,
):
    # Handle input variables before moving on to function logic
    if names == [] and total_indiv is not None:
        names = list(map(str, range(total_indiv)))

    # Initialize namespace variables
    remaining = names.copy()
    random.shuffle(remaining)

    if together is not None:
        groups = _create_groups(together)
        if apart is not None:
            groups_separated = _separate_individuals(groups, apart)
        else:
            groups_separated = groups
    else:
        groups_separated = []

    grouped_students = list(chain(*groups_separated))
    for student in grouped_students:
        remaining.remove(student)
    for student in remaining:
        _balance_nested_list(
            groups_separated, student, max_size=max_size, max_num_tables=max_tables
        )

    return groups_separated

    # Seat students together
    # if len(groups_separated) > len(seating):
    #     raise ValueError("More groups than clusters")
    # if max(groups_separated) > max(seating):
    #     raise ValueError("Groups are larger than allotted clusters")

    # TODO: Rather than fitting groups into existing clusters, I should write a
    #       function that takes a nested list and concatenates items on to the
    #       inner lists so that they maintain balance. I can pass a max_size
    #       parameter that would trigger appending a new list, or a
    #       max_num_tables parameter that would prevent the former process
    #       after a certain point.
    #
    #       From there, I can work with the existing `groups_separated` object
    #       and pull from the `remaining` list

    # for i, group in enumerate(groups_separated):
    #     empty_seats = seating[i].count(None)
    #     if len(group) > empty_seats:
    #         raise ValueError("Not enough empty seats")

    #     clear_seats = [s for s, x in enumerate(seating[i]) if x is None]
    #     for s, indiv in enumerate(group):
    #         seating[i][clear_seats[s]] = indiv
    #         remaining.remove(indiv)


# names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
# layout = [3, 4, 3]
# together = [["a", "b"], ["a", "e"], ["d", "g"]]
# apart = [["a", "d"], ["d", "f"]]


def _create_groups(together: list):
    """Returns unions of pairs

    Args:
        together (list): Pairs of individuals who should be together

    Returns:
        list: Nested list of groups, ordered largest to smallest
    
    Example:
        >>> together = [["a", "b"], ["a", "e"], ["d", "g"]]
        >>> _create_groups(together)
        
        >>> [["a", "b", "e"], ["d", "g"]]
    """
    groups = []

    for pair in together:
        if groups == []:
            groups.append(pair)
            continue

        bool_union = False
        for group in groups:
            intersect = list(set(pair) & set(group))

            if intersect != []:
                union = list(set(pair) | set(group))
                groups.remove(group)
                groups.append(union)
                bool_union = True
                break

        if not bool_union:
            groups.append(pair)

    groups.sort(key=len, reverse=True)
    return groups


def _get_nested_position(var, chart):
    # Find position in nested list
    idx = [chart.index(i) for i in chart if var in i]
    if len(idx) == 1:
        return idx[0]
    if len(idx) == 0:
        return None
    else:
        raise KeyError("Value occurrs more than once")


def _append_item(var, chart, apart):
    """Append var to chart, verifying that it obeys groups and separation rules
    
    Args:
        var (str): [description]
        chart (list): [description]
        apart (list): [description]
    """

    appended = False
    for i, group in enumerate(chart):
        if var not in group:

            kosher = True
            for a_pair in apart:
                if var not in a_pair:
                    continue

                a_pair = a_pair.copy()
                a_pair.remove(var)
                other_var = a_pair[0]

                if other_var in group:
                    kosher = False
                    break

            if kosher:
                chart[i] += var
                appended = True
                break

        if appended:
            break

    if not appended:
        chart.append([var])


def _separate_individuals(groups: list, apart: list) -> list:
    """[summary]

    Args:
        groups (list): [description]
        apart (list): [description]

    Raises:
        KeyError: [description]

    Returns:
        list: [description]

    Example:
        >>> groups = [["a", "b", "c"], ["d", "e", "f"]]
        >>> apart = [["a", "f"], ["d", "g"]]
        >>> _separate_individuals(groups, apart)
        >>> [["a", "b", "c", "g"], ["d", "e", "f"]]

        >>> groups = [["a", "b", "c"], ["d", "e", "f"]]
        >>> apart = [["a", "f"], ["d", "g"], ["a", "g"]]
        >>> _separate_individuals(groups, apart)
        >>> [["a", "b", "c"], ["d", "e", "f"], ["g"]]
    """

    chart = groups.copy()

    for pair in apart:
        item_1, item_2 = pair
        pos_1, pos_2 = list(map(lambda i: _get_nested_position(i, chart), pair))

        # 1. chart is empty
        if chart == []:
            chart.append([item_1])
            chart.append([item_2])

        # 2. pair is already grouped, and members are in different lists; good!
        if pos_1 is not None and pos_2 is not None and pos_1 != pos_2:
            continue

        # 3. One pair member is grouped, other remaining
        if ((pos_1 is None) ^ (pos_2 is None)) and (
            (pos_1 is not None) ^ (pos_2 is not None)
        ):
            remaining_item = item_1 if pos_1 is None else item_2
            _append_item(remaining_item, chart, apart)

        # 4. Both remaining
        if pos_1 is None and pos_2 is None:
            _append_item(item_1, chart, apart)
            _append_item(item_2, chart, apart)

    return chart


def _balance_nested_list(
    nested, item, max_size=float("Inf"), max_num_tables=float("Inf")
):
    """[summary]

    Args:
        nested ([type]): [description]
        item ([type]): [description]
        max_size ([type], optional): Defaults to float("Inf"). [description]
        max_num_tables ([type], optional): Defaults to float("Inf"). [description]
    """

    nested_size = [len(i) for i in nested]
    all_same_len = len(set(nested_size)) == 1
    min_nested_size = min(nested_size)
    max_nested_size = max(nested_size)
    num_tables = len(nested)
    min_index = nested_size.index(min(nested_size))

    if num_tables >= max_num_tables and max_nested_size >= max_size:
        raise ValueError(
            "Number of tables is greater than value specified by `max_num_tables` "
            "and group size is greater than value specified by `max_size`"
        )

    if all_same_len and max_nested_size >= max_size:
        nested.append([item])
    else:
        nested[min_index] += item
