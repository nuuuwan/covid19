"""Test."""
import unittest

from covid19 import lk_data


class TestCOVIDData(unittest.TestCase):
    """Tests."""

    def test_get_timeseries(self):
        """Test."""
        self.assertIn('cum_deaths', lk_data.get_timeseries()[0])
        self.assertNotIn('cdeaths', lk_data.get_timeseries()[0])


if __name__ == '__main__':
    unittest.main()
