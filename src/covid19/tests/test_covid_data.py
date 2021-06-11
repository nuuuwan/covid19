"""Test."""
import unittest

from covid19 import covid_data


class TestCOVIDData(unittest.TestCase):
    """Tests."""

    def test_load_jhu_data(self):
        """Test."""
        self.assertIn('Sri Lanka', covid_data.load_jhu_data())
        self.assertNotIn('Sri Lanka2', covid_data.load_jhu_data())

    def test_load_hpb_data(self):
        """Test."""
        self.assertIn('success', covid_data.load_hpb_data())
        self.assertNotIn('failure', covid_data.load_hpb_data())


if __name__ == '__main__':
    unittest.main()
