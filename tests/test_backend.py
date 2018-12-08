from .context import app
import unittest


class Backend_Test(unittest.TestCase):
    """Test cases for the seatingchart.backend module"""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

    def test_create_groups(self):
        groups = app.main.backend._create_groups([["Amy", "Bob"], ["Amy", "Dan"]])
        assert all([i in groups[0] for i in ["Amy", "Bob", "Dan"]])

        groups = app.main.backend._create_groups(None)
        assert groups == []

    def test_separate_individuals(self):
        groups = [["Amy", "Bob", "Carly"], ["Dan", "Eesha", "Frank"]]
        apart = [["Amy", "Frank"], ["Dan", "Grace"]]
        chart = app.main.backend._separate_individuals(groups, apart)
        assert chart == [["Amy", "Bob", "Carly", "Grace"], ["Dan", "Eesha", "Frank"]]

        groups = [["Amy", "Bob", "Carly"], ["Dan", "Eesha", "Frank"]]
        apart = [["Amy", "Frank"], ["Dan", "Grace"], ["Amy", "Grace"]]
        chart = app.main.backend._separate_individuals(groups, apart)
        assert chart == [["Amy", "Bob", "Carly"], ["Dan", "Eesha", "Frank"], ["Grace"]]

        groups = []
        apart = None
        chart = app.main.backend._separate_individuals(groups, apart)
        assert chart == []

    def test_append_item(self):
        chart = [["Amy", "Bob", "Carly"], ["Dan", "Eesha"]]
        apart = [
            ["Carly", "Dan"],
            ["Frank", "Eesha"],
            ["Frank", "Grace"],
            ["Frank", "Henry"],
            ["Bob", "Immanuel"],
        ]
        max_size = 4

        app.main.backend._append_item("Frank", chart, apart, max_size)
        assert chart == [["Amy", "Bob", "Carly", "Frank"], ["Dan", "Eesha"]]

        app.main.backend._append_item("Grace", chart, apart, max_size)
        assert chart == [["Amy", "Bob", "Carly", "Frank"], ["Dan", "Eesha", "Grace"]]

        app.main.backend._append_item("Henry", chart, apart, max_size)
        assert chart == [
            ["Amy", "Bob", "Carly", "Frank"],
            ["Dan", "Eesha", "Grace", "Henry"],
        ]

        app.main.backend._append_item("Immanuel", chart, apart, max_size)
        assert chart == [
            ["Amy", "Bob", "Carly", "Frank"],
            ["Dan", "Eesha", "Grace", "Henry"],
            ["Immanuel"],
        ]

    def test_balance_nested_list(self):
        value = "1"

        nested_1 = [["0", "0", "0", "0"], ["0", "0", "0"], ["0", "0"]]
        app.main.backend._balance_nested_list(nested_1, value)
        assert nested_1 == [["0", "0", "0", "0"], ["0", "0", "0"], ["0", "0", "1"]]

        nested_2 = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        app.main.backend._balance_nested_list(nested_2, value, max_size=3)
        assert nested_2 == [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"], ["1"]]

        nested_3 = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        app.main.backend._balance_nested_list(nested_3, value, num_groups=3)
        assert nested_3 == [["0", "0", "0", "1"], ["0", "0", "0"], ["0", "0", "0"]]

    def test_create_seating_chart(self):
        names = [
            "Amy",
            "Bob",
            "Carly",
            "Dan",
            "Eesha",
            "Frank",
            "Grace",
            "Henry",
            "Immanuel",
            "James",
            "Kevin",
        ]
        together = [
            ["Amy", "Bob"],
            ["Amy", "Eesha"],
            ["Bob", "Eesha"],
            ["Frank", "Grace"],
        ]
        apart = [["Amy", "Frank"], ["Dan", "Grace"], ["Amy", "Grace"]]
        max_tables = float("Inf")

        chart_1 = app.main.backend.create_seating_chart(names, together.copy(), apart)
        assert len(chart_1) <= max_tables
        assert max([len(i) for i in chart_1]) <= float("Inf")

        ms_2 = 4
        together = [
            ["Amy", "Bob"],
            ["Amy", "Eesha"],
            ["Bob", "Eesha"],
            ["Frank", "Grace"],
        ]
        chart_2 = app.main.backend.create_seating_chart(
            names, together.copy(), apart, max_size=ms_2
        )
        assert len(chart_2) <= max_tables
        assert max([len(i) for i in chart_2]) <= ms_2

        chart_3 = app.main.backend.create_seating_chart(
            names, None, None, max_size=4, num_groups=3
        )
        assert len(chart_3) == 3
        assert max([len(i) for i in chart_3]) <= 4

    def test_handle_form_individuals(self):
        inpt = "Amy\n\rBob,Carly;Dan\nEesha\rFrank"
        output = ["Amy", "Bob", "Carly", "Dan", "Eesha", "Frank"]
        assert app.main.backend.handle_form_individuals(inpt) == output

    def test_handle_form_groupings(self):
        assert app.main.backend.handle_form_groupings(None) is None
        assert app.main.backend.handle_form_groupings("") is None

        inpt = "Amy,Bob\n\rCarly,Dan"
        output = [["Amy", "Bob"], ["Carly", "Dan"]]
        assert app.main.backend.handle_form_groupings(inpt) == output

    def test_handle_form_integer(self):
        assert app.main.backend.handle_form_integer(0) == float("Inf")
        assert app.main.backend.handle_form_integer(1) == 1

    def test_render_output(self):
        inpt = [["Amy", "Bob"], ["Carly", "Dan"]]
        output = "Amy, Bob\n\rCarly, Dan"
        assert app.main.backend.render_output(inpt) == output
