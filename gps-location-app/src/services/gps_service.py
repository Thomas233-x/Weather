class GPSService:
    def __init__(self, gps_provider):
        self.gps_provider = gps_provider
        self.is_tracking = False

    def start_tracking(self):
        if not self.is_tracking:
            self.gps_provider.start_location_updates()
            self.is_tracking = True

    def stop_tracking(self):
        if self.is_tracking:
            self.gps_provider.stop_location_updates()
            self.is_tracking = False

    def get_current_location(self):
        return self.gps_provider.get_current_location()