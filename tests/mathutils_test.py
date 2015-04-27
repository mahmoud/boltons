import unittest
import boltons.mathutils as bmu


class TestCeilAndFloor(unittest.TestCase):

    def setUp(self):
        self.BIG_LIST = [1618, 1378, 166, 1521, 2347, 2016, 879, 2123, 269.3, 1230, 66, 425.2, 250, 2399, 2314, 439,
                         247, 208, 379, 1861]
        self.BIG_LIST_SORTED = sorted(self.BIG_LIST)
        self.OUT_OF_RANGE_LOWER = 60
        self.OUT_OF_RANGE_UPPER = 2500
        self.VALID_LOWER = self.BIG_LIST_SORTED[3]
        self.VALID_UPPER = self.BIG_LIST_SORTED[-3]
        self.VAILD_BETWEEN = 248.5

    # Tests for boltons.mathutils.ceil_from_iter()
    def test_ceil_from_iter_default(self):
        self.assertEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_LOWER), self.VALID_LOWER)
        self.assertEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_UPPER), self.VALID_UPPER)

    def test_ceil_from_iter_default_allow_equal_false(self):
        self.assertNotEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_LOWER, allow_equal=False), self.VALID_LOWER)
        self.assertNotEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_UPPER, allow_equal=False), self.VALID_UPPER)

    def test_ceil_from_iter_unsorted(self):
        self.assertEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_LOWER),
                         bmu.ceil_from_iter(self.BIG_LIST_SORTED, self.VALID_LOWER))

        self.assertEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_UPPER),
                         bmu.ceil_from_iter(self.BIG_LIST_SORTED, self.VALID_UPPER))

    def test_ceil_from_iter_unsorted_failure(self):
        self.assertNotEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_LOWER),
                            bmu.ceil_from_iter(self.BIG_LIST_SORTED, self.VALID_LOWER, sorted_src=True))

        self.assertNotEqual(bmu.ceil_from_iter(self.BIG_LIST, self.VALID_UPPER),
                            bmu.ceil_from_iter(self.BIG_LIST_SORTED, self.VALID_UPPER, sorted_src=True))

    def test_ceil_from_iter_sorted(self):
        self.assertEqual(bmu.ceil_from_iter(self.BIG_LIST_SORTED, self.VALID_LOWER), self.VALID_LOWER)
        self.assertEqual(bmu.ceil_from_iter(self.BIG_LIST_SORTED, self.VALID_UPPER), self.VALID_UPPER)

    def test_ceil_from_iter_exception_out_of_range_lower(self):
        expected = min(self.BIG_LIST)
        actual = bmu.ceil_from_iter(self.BIG_LIST, self.OUT_OF_RANGE_LOWER)
        self.assertEqual(expected, actual)

    def test_ceil_from_iter_exception_out_of_range_upper(self):
        self.assertRaises(ValueError, bmu.ceil_from_iter, self.BIG_LIST, self.OUT_OF_RANGE_UPPER)

    # Tests for boltons.mathutils.floor_from_iter()
    def test_floor_from_iter_default(self):
        self.assertEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_LOWER), self.VALID_LOWER)
        self.assertEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_UPPER), self.VALID_UPPER)

    def test_floor_from_iter_default_allow_equal_false(self):
        self.assertNotEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_LOWER, allow_equal=False), self.VALID_LOWER)
        self.assertNotEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_UPPER, allow_equal=False), self.VALID_UPPER)

    def test_floor_from_iter_unsorted(self):
        self.assertEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_LOWER),
                         bmu.floor_from_iter(self.BIG_LIST_SORTED, self.VALID_LOWER))

        self.assertEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_UPPER),
                         bmu.floor_from_iter(self.BIG_LIST_SORTED, self.VALID_UPPER))

    def test_floor_from_iter_unsorted_failure(self):
        self.assertNotEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_LOWER),
                            bmu.floor_from_iter(self.BIG_LIST_SORTED, self.VALID_LOWER, sorted_src=True))

        self.assertNotEqual(bmu.floor_from_iter(self.BIG_LIST, self.VALID_UPPER),
                            bmu.floor_from_iter(self.BIG_LIST_SORTED, self.VALID_UPPER, sorted_src=True))

    def test_floor_from_iter_sorted(self):
        self.assertEqual(bmu.floor_from_iter(self.BIG_LIST_SORTED, self.VALID_LOWER), self.VALID_LOWER)
        self.assertEqual(bmu.floor_from_iter(self.BIG_LIST_SORTED, self.VALID_UPPER), self.VALID_UPPER)

    def test_floor_from_iter_exception_out_of_range_lower(self):
        self.assertRaises(ValueError, bmu.floor_from_iter, self.BIG_LIST, self.OUT_OF_RANGE_LOWER)

    def test_floor_from_iter_exception_out_of_range_upper(self):
        expected = max(self.BIG_LIST)
        actual = bmu.floor_from_iter(self.BIG_LIST, self.OUT_OF_RANGE_UPPER)
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()