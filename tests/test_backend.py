from .context import app
import unittest


class Backend_Test(unittest.TestCase):
    """Test cases for the seatingchart.backend module"""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

    def test_create_groups(self):
        groups = app.main.backend._create_groups([["a", "b"], ["a", "d"]])
        assert all([i in groups[0] for i in ["a", "b", "d"]])

    def test_separate_individuals(self):
        groups = [["a", "b", "c"], ["d", "e", "f"]]
        apart = [["a", "f"], ["d", "g"]]
        chart = app.main.backend._separate_individuals(groups, apart)
        assert chart == [["a", "b", "c", "g"], ["d", "e", "f"]]

        groups = [["a", "b", "c"], ["d", "e", "f"]]
        apart = [["a", "f"], ["d", "g"], ["a", "g"]]
        chart = app.main.backend._separate_individuals(groups, apart)
        assert chart == [["a", "b", "c"], ["d", "e", "f"], ["g"]]

    def test_append(self):
        chart = [["a", "b", "c"], ["d", "e"]]
        apart = [["c", "d"], ["f", "e"], ["f", "g"], ["f", "h"], ["b", "i"]]
        max_size = 4

        app.main.backend._append_item("f", chart, apart, max_size)
        assert chart == [["a", "b", "c", "f"], ["d", "e"]]

        app.main.backend._append_item("g", chart, apart, max_size)
        assert chart == [["a", "b", "c", "f"], ["d", "e", "g"]]

        app.main.backend._append_item("h", chart, apart, max_size)
        assert chart == [["a", "b", "c", "f"], ["d", "e", "g", "h"]]

        app.main.backend._append_item("i", chart, apart, max_size)
        assert chart == [["a", "b", "c", "f"], ["d", "e", "g", "h"], ["i"]]

    def test_balance_nested_list(self):
        value = "1"

        nested_1 = [["0", "0", "0", "0"], ["0", "0", "0"], ["0", "0"]]
        app.main.backend._balance_nested_list(nested_1, value)
        assert nested_1 == [["0", "0", "0", "0"], ["0", "0", "0"], ["0", "0", "1"]]

        nested_2 = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        app.main.backend._balance_nested_list(nested_2, value, max_size=3)
        assert nested_2 == [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"], ["1"]]

        nested_3 = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        app.main.backend._balance_nested_list(nested_3, value, max_num_tables=3)
        assert nested_3 == [["0", "0", "0", "1"], ["0", "0", "0"], ["0", "0", "0"]]

    def test_create_seating_chart(self):
        names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]
        together = [["a", "b"], ["a", "e"], ["b", "e"], ["f", "g"]]
        apart = [["a", "f"], ["d", "g"], ["a", "g"]]
        max_tables = float("Inf")

        chart_1 = app.main.backend.create_seating_chart(names, together.copy(), apart)
        assert len(chart_1) <= max_tables
        assert max([len(i) for i in chart_1]) <= float("Inf")

        ms_2 = 4
        together = [["a", "b"], ["a", "e"], ["b", "e"], ["f", "g"]]
        chart_2 = app.main.backend.create_seating_chart(names, together.copy(), apart, max_size=ms_2)
        assert len(chart_2) <= max_tables
        assert max([len(i) for i in chart_2]) <= ms_2

    def test_handle_form_individuals(self):
        inpt = "A\n\rB,C;D\nE\rF"
        output = ["A", "B", "C", "D", "E", "F"]
        assert app.main.backend.handle_form_individuals(inpt) == output

    def test_handle_form_groupings(self):
        assert app.main.backend.handle_form_groupings(None) is None
        assert app.main.backend.handle_form_groupings("") is None

        inpt = "A,B\n\rC,D"
        output = [["A", "B"], ["C", "D"]]
        assert app.main.backend.handle_form_groupings(inpt) == output

    def test_handle_form_integer(self):
        assert app.main.backend.handle_form_integer(0) == float("Inf")
        assert app.main.backend.handle_form_integer(1) == 1

    def test_render_output(self):
        inpt = [["A", "B"], ["C", "D"]]
        output = "A, B\n\rC, D"
        assert app.main.backend.render_output(inpt) == output
