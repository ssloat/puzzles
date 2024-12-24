import unittest

from collatz import seq, longest_collatz

class TestCollatz(unittest.TestCase):
    def test_5(self):
        result = seq(5)
        self.assertEqual(result, [5, 16, 8, 4, 2, 1])

    def test_longest(self):
        result = longest_collatz(20)
        self.assertEqual(result.num, 18)
        self.assertEqual(
            result.seq, 
            [
                18, 9, 28, 14, 7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 
                10, 5, 16, 8, 4, 2, 1
            ]
        )


if __name__ == '__main__':
    unittest.main()
