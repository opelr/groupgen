from .context import seatingchart
import unittest


class Backend_Test(unittest.TestCase):
    """Test cases for the seatingchart.backend module"""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

    def test_create_groups(self):
        groups = seatingchart.backend._create_groups([["a", "b"], ["a", "d"]])
        assert all([i in groups[0] for i in ["a", "b", "d"]])

    def test_separate_individuals(self):
        groups = [["a", "b", "c"], ["d", "e", "f"]]
        apart = [["a", "f"], ["d", "g"]]
        chart = seatingchart.backend._separate_individuals(groups, apart)
        assert chart == [["a", "b", "c", "g"], ["d", "e", "f"]]

        groups = [["a", "b", "c"], ["d", "e", "f"]]
        apart = [["a", "f"], ["d", "g"], ["a", "g"]]
        chart = seatingchart.backend._separate_individuals(groups, apart)
        assert chart == [["a", "b", "c"], ["d", "e", "f"], ["g"]]

    def test_balance_nested_list(self):
        value = "1"

        nested_1 = [["0", "0", "0", "0"], ["0", "0", "0"], ["0", "0"]]
        seatingchart.backend._balance_nested_list(nested_1, value)
        assert nested_1 == [["0", "0", "0", "0"], ["0", "0", "0"], ["0", "0", "1"]]

        nested_2 = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        seatingchart.backend._balance_nested_list(nested_2, value, max_size=3)
        assert nested_2 == [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"], ["1"]]

        nested_3 = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        seatingchart.backend._balance_nested_list(nested_3, value, max_num_tables=3)
        assert nested_3 == [["0", "0", "0", "1"], ["0", "0", "0"], ["0", "0", "0"]]

    def test_create_seating_chart(self):
        names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]
        together = [["a", "b"], ["a", "e"], ["d", "g"], ["f", "g"]]
        apart = [["a", "f"], ["d", "g"], ["a", "g"]]
        max_tables = float("Inf")
        
        max_size_1 = float("Inf")
        chart_1 = seatingchart.backend.create_seating_chart(names, together, apart)
        assert len(chart_1) <= max_tables
        assert max([len(i) for i in chart_1]) <= max_size_1

        max_size_2 = 4
        chart_2 = seatingchart.backend.create_seating_chart(names, together, apart, max_size=max_size_2)
        assert len(chart_2) <= max_tables
        assert max([len(i) for i in chart_2]) <= max_size_2