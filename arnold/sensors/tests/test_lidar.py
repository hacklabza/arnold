from arnold.config import SENSOR_CONFIG


class TestLidar:

    def setup_method(self, method):
        self.config = SENSOR_CONFIG['lidar']

    def test_config(self):
        for config_key in ['serial_port', 'baudrate']:
            assert config_key in self.config

    def test_get_distance(self):
        # TODO: Figure out how to mock Serial
        pass
