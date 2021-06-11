"""Test."""
import unittest

from covid19 import lk_data


class TestCOVIDData(unittest.TestCase):
    """Tests."""

    def test_load_hpb_data_raw(self):
        """Test."""
        data = lk_data.load_hpb_data_raw()
        self.assertIn('success', data)
        self.assertNotIn('failure', data)

    def test_get_timeseries(self):
        """Test."""
        data = lk_data.get_timeseries()[0]
        self.assertIn('cum_deaths', data)
        self.assertIn('new_pcr_tests', data)
        self.assertNotIn('cdeaths', data)


if __name__ == '__main__':
    unittest.main()
