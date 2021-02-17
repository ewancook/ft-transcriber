import unittest
from collections import namedtuple

from fastdbf import parsing_sequences as ps


class TestSkipSequences(unittest.TestCase):
    def setUp(self):
        field = namedtuple("field", ["name", "length"])
        self.all_fields = [
            field("Date", 8),
            field("Time", 8),
            field("Millitm", 3),
            field("TagIndex", 5),
            field("Value", 8),
            field("Status", 1),
            field("Marker", 1),
            field("Internal", 4),
        ]
        self.tag_fields = [
            field("Tagname", 255),
            field("TTagIndex", 5),
            field("TagType", 1),
            field("TagDataTyp", 2),
        ]

    def test_float_field_parsing_sequence_first_row(self):
        sequence = ps.float_field_parsing_sequence_first_row(self.all_fields)
        expected = [
            ("Date", 0, 8),
            ("Time", 8, 16),
            [False, 16, 24],
            ("Value", 24, 32),
            [False, 32, 33],
            ("Marker", 33, 34),
            [False, 34, 38],
        ]
        self.assertEqual(expected, sequence)

    def test_float_field_parsing_sequence_later_rows(self):
        sequence = ps.float_field_parsing_sequence_later_rows(self.all_fields)
        expected = [
            [False, 0, 24],
            ("Value", 24, 32),
            [False, 32, 38],
        ]
        self.assertEqual(expected, sequence)

    def test_float_field_parsing_sequence_counting(self):
        sequence = ps.float_field_parsing_sequence_counting(self.all_fields)
        expected = [
            ("Date", 0, 8),
            ("Time", 8, 16),
            [False, 16, 19],
            ("TagIndex", 19, 24),
            ("Value", 24, 32),
            [False, 32, 33],
            ("Marker", 33, 34),
            [False, 34, 38],
        ]
        self.assertEqual(expected, sequence)

    def test_tag_field_parsing_sequence(self):
        sequence = ps.tag_field_parsing_sequence(self.tag_fields)
        expected = [
            ("Tagname", 0, 255),
            ("TTagIndex", 255, 260),
            [False, 260, 263],
        ]
        self.assertEqual(expected, sequence)

    def test_float_row_parsing_sequence(self):
        row_length = 38
        first_row_seq = ps.float_field_parsing_sequence_first_row(
            self.all_fields
        )
        later_rows_seq = ps.float_field_parsing_sequence_later_rows(
            self.all_fields
        )
        results = [
            (
                ([1, 2, 3], [1, 2, 3]),
                [
                    (True, row_length - 1, first_row_seq),
                    [False, 1, None],
                    (True, row_length - 1, later_rows_seq),
                    [False, 1, None],
                    (True, row_length - 1, later_rows_seq),
                ],
            ),
            (
                ([1, 3], [1, 2, 3]),
                [
                    (True, row_length - 1, first_row_seq),
                    [False, row_length + 1, None],
                    (True, row_length - 1, later_rows_seq),
                ],
            ),
            (
                ([1, 2], [1, 2, 3]),
                [
                    (True, row_length - 1, first_row_seq),
                    [False, 1, None],
                    (True, row_length - 1, later_rows_seq),
                    [False, row_length, None],
                ],
            ),
            (
                ([2, 3], [1, 2, 3]),
                [
                    [False, row_length, None],
                    (True, row_length - 1, first_row_seq),
                    [False, 1, None],
                    (True, row_length - 1, later_rows_seq),
                ],
            ),
            (
                ([1], [1, 2, 3]),
                [
                    (True, row_length - 1, first_row_seq),
                    [False, row_length * 2, None],
                ],
            ),
            (
                ([2], [1, 2, 3]),
                [
                    [False, row_length, None],
                    (True, row_length - 1, first_row_seq),
                    [False, row_length, None],
                ],
            ),
            (
                ([3], [1, 2, 3]),
                [
                    [False, row_length * 2, None],
                    (True, row_length - 1, first_row_seq),
                ],
            ),
            (
                ([4], [1, 2, 3]),
                [
                    [False, row_length * 3 - 1, None],
                ],
            ),
        ]
        for args, result in results:
            expected = ps.float_row_parsing_sequence(
                row_length, *args, self.all_fields
            )
            self.assertEqual(expected, result)
