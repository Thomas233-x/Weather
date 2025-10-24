import gps
import time

class GPSProvider:
    def __init__(self):
        self.session = gps.gps(mode=gps.WATCH_ENABLE)  # Start GPS session
        self.current_location = None

    def get_location(self):
        """Retrieve the current GPS location."""
        try:
            self.session.next()  # Wait for the next available GPS data
            self.current_location = {
                'latitude': self.session.fix.latitude,
                'longitude': self.session.fix.longitude,
                'altitude': self.session.fix.altitude,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.session.fix.time))
            }
            return self.current_location
        except Exception as e:
            print(f"Error retrieving GPS data: {e}")
            return None

    def stop(self):
        """Stop the GPS session."""
        self.session = None  # Clean up the session when done