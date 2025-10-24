import unittest
from src.gps_provider import GPSProvider
from src.services.gps_service import GPSService

class TestGPSFunctionality(unittest.TestCase):

    def setUp(self):
        self.gps_provider = GPSProvider()
        self.gps_service = GPSService(self.gps_provider)

    def test_get_current_location(self):
        location = self.gps_service.get_current_location()
        self.assertIsNotNone(location)
        self.assertIn('latitude', location)
        self.assertIn('longitude', location)

    def test_start_location_updates(self):
        self.gps_service.start_location_updates()
        self.assertTrue(self.gps_provider.is_updating)

    def test_stop_location_updates(self):
        self.gps_service.start_location_updates()
        self.gps_service.stop_location_updates()
        self.assertFalse(self.gps_provider.is_updating)

if __name__ == '__main__':
    unittest.main()