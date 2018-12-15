"""
seatingchart.backend
~~~~~~~~~~~~~~~~~~~~

This module contains code for generating the primary functional logic of this
application.
"""

import random
from itertools import chain
import re
import json


def create_seating_chart(
    names: list,
    together=None,
    apart=None,
    max_size=float("Inf"),
    num_groups=float("Inf"),
):
    """Returns nested list of names that meet grouping parameters

    Args:
        names (list): Individuals we are grouping. Each name must be unique
        together (list, optional): Defaults to None. List of pairwise explicit grouped individuals.
        apart (list, optional): Defaults to None. List of pairwise explicit separated individuals.
        max_size (int, optional): Defaults to float("Inf"). Maximum size for a single group.
        num_groups (int, optional): Defaults to float("Inf"). Number of groups.

    Returns:
        list: Nested list with entries for each group

    Example:
        >>> names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]
        >>> together = [["a", "b"], ["a", "e"], ["d", "g"], ["f", "g"]]
        >>> apart = [["a", "f"], ["a", "g"]]
        >>> max_size = 4
        >>> create_seating_chart(names, together, apart, max_size=max_size)
        [['e', 'b', 'a', 'c'], ['g', 'd', 'f', 'j'], ['k', 'h', 'i']]
    """
    # Initialize namespace variables
    remaining = names.copy()
    random.shuffle(remaining)

    if (
        apart is not None
        and together is not None
        and any([i in apart for i in together])
    ):
        raise ValueError("Cannot have overlap in `together` and `apart`")

    groups = _create_groups(together)
    groups_sep = _separate_individuals(groups, apart, max_size)

    if groups_sep != []:
        if max_size < max([len(g) for g in groups_sep]):
            raise ValueError("Group too big")

    grouped_students = list(set(chain(*groups_sep)))
    for student in grouped_students:
        remaining.remove(student)
    for student in remaining:
        _balance_nested_list(
            groups_sep, student, max_size=max_size, num_groups=num_groups
        )

    if len(groups_sep) > num_groups:
        raise ValueError(
            "Group definitions do not allow for the ..."
            "Please change the number of groups or the group/separates definitions"
        )

    return groups_sep


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
    if together is None:
        return groups

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


def _append_item(var: str, chart: list, apart: list, max_size):
    """Append var to chart, verifying that it obeys groups and separation rules

    Args:
        var (str): Variable being appended
        chart (list): Nested list
        apart (list): List of pairwise separation rules
        max_size [(type)]: [descrition]
    """

    appended = False
    for i, group in enumerate(chart):
        if var not in group:

            kosher = True
            for a_pair in apart:
                if var not in a_pair:
                    continue

                b_pair = a_pair.copy()
                b_pair.remove(var)
                other_var = b_pair[0]

                if other_var in group:
                    kosher = False
                    break

            if kosher:
                if len(group) >= max_size:
                    break
                chart[i] += [var]
                appended = True
                break

        if appended:
            break

    if not appended:
        chart.append([var])


def _separate_individuals(groups: list, apart: list, max_size=float("Inf")) -> list:
    """Explicit handling of separated individuals

    Args:
        groups (list): Nested list representing groups
        apart (list): Nested list of explicit pairwise separations
        max_size [(type)]: [descrition]

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

    chart = [i[:] for i in groups]

    if apart is None:
        return chart

    for pair in apart:
        item_1, item_2 = pair
        pos_1, pos_2 = list(map(lambda i: _get_nested_position(i, chart), pair))

        # 1. chart is empty
        if chart == []:
            return [[item_1], [item_2]]

        # 2. pair is already grouped, and members are in different lists; good!
        elif pos_1 is not None and pos_2 is not None and pos_1 != pos_2:
            continue

        # 3. One pair member is grouped, other remaining
        elif ((pos_1 is None) ^ (pos_2 is None)) and (
            (pos_1 is not None) ^ (pos_2 is not None)
        ):
            remaining_item = item_1 if pos_1 is None else item_2
            _append_item(remaining_item, chart, apart, max_size)

        # 4. Both remaining
        elif pos_1 is None and pos_2 is None:
            _append_item(item_1, chart, apart, max_size)
            _append_item(item_2, chart, apart, max_size)

    return chart


def _balance_nested_list(
    nested: list, item: str, max_size=float("Inf"), num_groups=float("Inf")
):
    """Balances a nested list, respecting max size and number of internal lists

    Args:
        nested (list): Nested list
        item (str): Item to be added
        max_size (int, optional): Defaults to float("Inf"). Maximum size for a single group.
        num_groups (int, optional): Defaults to float("Inf"). Maximum number of groups.
    """
    if nested == []:
        nested.append([item])
        return

    nested_size = [len(i) for i in nested]
    all_same_len = len(set(nested_size)) == 1
    max_nested_size = max(nested_size)
    num_current_groups = len(nested)
    min_index = nested_size.index(min(nested_size))

    if max_nested_size > max_size:
        raise ValueError("Largest group exceeds `max_size` parameter")
    if num_current_groups > num_groups and max_nested_size > max_size:
        raise ValueError(
            "Number of tables is greater than value specified by `num_groups` "
            "and group size is greater than value specified by `max_size`"
        )

    if num_groups != float("Inf") and num_current_groups < num_groups:
        nested.append([item])
    elif all_same_len and (max_nested_size >= max_size):
        nested.append([item])
    else:
        nested[min_index] += [item]


def render_output(out: list):
    """Pretty's `create_seating_chart` output

    Args:
        out (list): Output of `create_seating_chart`

    Returns:
        str: Prettified output for presentation to user
    """
    return "\n\r".join([", ".join(i) for i in out])


def store_display(names: list):
    """Converts a list of strings to a fixed-width (40) string
    
    Args:
        names (list): List of strings to join
    
    Returns:
        str: Joined and concatenated string for displaying
    """
    joined = ", ".join([i.strip() for i in names.split("\n")])
    if len(joined) > 40:
        return f"{joined:.37}" + "..."
    return joined


def form_to_function(input_str, category):
    if not category in ["individuals", "groupings", "integers"]:
        raise KeyError(
            "'category' must of one of: 'individuals', 'groupings', or 'integers'"
        )

    if category == "individuals":
        return list(re.split("[,;\n\r]+", input_str))

    elif category == "groupings":
        if input_str is None or input_str == "":
            return None

        nest = [i.split(",") for i in re.split("[\n\r]+", input_str)]
        return [[i.strip() for i in j] for j in nest]

    else:
        return float("Inf") if input_str == 0 else input_str


def form_to_model(input_str, category):
    if not category in ["individuals", "groupings"]:
        raise KeyError("'category' must of one of: 'individuals' or 'groupings'")

    return json.dumps(form_to_function(input_str, category))


def model_to_form(input_str, category):
    if not category in ["individuals", "groupings", "integers"]:
        raise KeyError(
            "'category' must of one of: 'individuals', 'groupings', or 'integers'"
        )

    if category == "individuals":
        return "\n".join(json.loads(input_str))
    elif category == "groupings":
        input_str = json.loads(input_str)
        if input_str is None or input_str == []:
            return ""
        return "\n".join([", ".join(i) for i in input_str])
    else:
        return 0 if input_str == float("Inf") else input_str
