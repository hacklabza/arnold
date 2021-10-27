from arnold import config


class TestIMU:

    def setup_method(self, method):
        self.config = config.SENSOR['imu']

    def test_config(self):
        for config_key in ['address', 'orientation']:
            assert config_key in self.config

    def test_get_accelerometer_data(self):
        # TODO: Figure out how to mock smbus
        pass

    def test_get_gyroscope_data(self):
        # TODO: Figure out how to mock smbus
        pass

    def test_get_magnetometer_data(self):
        # TODO: Figure out how to mock smbus
        pass

    def test_get_temperature(self):
        # TODO: Figure out how to mock smbus
        pass
