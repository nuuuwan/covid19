"""Test."""
import unittest

from utils.cache import cache

from covid19 import covid_data


class TestCOVIDData(unittest.TestCase):
    """Tests."""

    def test_load_jhu_data(self):
        """Test."""
        data = covid_data.load_jhu_data()
        self.assertIn('LK', data)
        self.assertNotIn('Sri Lanka2', data)


if __name__ == '__main__':
    unittest.main()
