"""
seatingchart.backend
~~~~~~~~~~~~~~~~~~~~

This module contains code for generating the primary functional logic of this
application.
"""

import random
from itertools import chain
import re


def create_seating_chart(
    names: list,
    together=None,
    apart=None,
    max_size=float("Inf"),
    max_tables=float("Inf"),
):
    """Returns nested list of names that meet grouping parameters

    Args:
        names (list): Individuals we are grouping. Each name must be unique
        together (list, optional): Defaults to None. List of pairwise explicit grouped individuals.
        apart (list, optional): Defaults to None. List of pairwise explicit separated individuals.
        max_size (int, optional): Defaults to float("Inf"). Maximum size for a single group.
        max_tables (int, optional): Defaults to float("Inf"). Maximum number of groups.

    Returns:
        list: Nested list with entries for each group

    Example:
        >>> names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]
        >>> together = [["a", "b"], ["a", "e"], ["d", "g"], ["f", "g"]]
        >>> apart = [["a", "f"], ["d", "g"], ["a", "g"]]
        >>> max_size = 4
        >>> create_seating_chart(names, together, apart, max_size=max_size)
        [['e', 'b', 'a', 'c'], ['g', 'd', 'f', 'j'], ['k', 'h', 'i']]
    """
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


def _create_groups(together: list):
    """Returns unions of pairs

    Args:
        together (list): Pairs of individuals who should be together

    Returns:
        list: Nested list of groups, ordered largest to smallest

    Example:
        >>> together = [["a", "b"], ["a", "e"], ["d", "g"]]
        >>> _create_groups(together)
        [["a", "b", "e"], ["d", "g"]]
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


def _get_nested_position(var: str, chart: list):
    """Finds position of a variable inside a nested list

    Args:
        var (str): Variable we're searching for
        chart (list): Nested list

    Returns:
        int: Index of nested list that contains `var`. Returns None if not found.
    """
    idx = [chart.index(i) for i in chart if var in i]
    if len(idx) == 1:
        return idx[0]
    if len(idx) == 0:
        return None
    else:
        raise KeyError("Value occurrs more than once")


def _append_item(var: str, chart: list, apart: list):
    """Append var to chart, verifying that it obeys groups and separation rules

    Args:
        var (str): Variable being appended
        chart (list): Nested list
        apart (list): List of pairwise separation rules
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
    """Explicit handling of separated individuals

    Args:
        groups (list): Nested list representing groups
        apart (list): Nested list of explicit pairwise separations

    Returns:
        list: Nested list of groups

    Example:
        >>> groups = [["a", "b", "c"], ["d", "e", "f"]]
        >>> apart = [["a", "f"], ["d", "g"]]
        >>> _separate_individuals(groups, apart)
        [["a", "b", "c", "g"], ["d", "e", "f"]]

        >>> groups = [["a", "b", "c"], ["d", "e", "f"]]
        >>> apart = [["a", "f"], ["d", "g"], ["a", "g"]]
        >>> _separate_individuals(groups, apart)
        [["a", "b", "c"], ["d", "e", "f"], ["g"]]
    """

    chart = groups.copy()

    if apart is None:
        return chart

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
    nested: list, item: str, max_size=float("Inf"), max_num_tables=float("Inf")
):
    """Balances a nested list, respecting max size and number of internal lists

    Args:
        nested (list): Nested list
        item (str): Item to be added
        max_size (int, optional): Defaults to float("Inf"). Maximum size for a single group.
        max_num_tables (int, optional): Defaults to float("Inf"). Maximum number of groups.
    """

    nested_size = [len(i) for i in nested]
    all_same_len = len(set(nested_size)) == 1
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


def handle_form_individuals(individuals):
    return list(re.split("[,;\n\r]+", individuals))


def handle_form_groupings(grouping):
    if grouping is None or grouping == "":
        return None

    nest = [i.split(",") for i in grouping.split("\n\r")]
    return [[i.strip() for i in j] for j in nest]


def handle_form_integer(i):
    return float("Inf") if i == 0 else i


def render_output(out: list):
    return "\n\r\n\r".join([", ".join(i) for i in out])
