from arnold.config import SENSOR_CONFIG


class TestMicrophone:

    def setup_method(self, method):
        self.config = SENSOR_CONFIG['microphone']

    def test_config(self):
        required_config = [
            'card_number', 'device_index', 'sample_rate', 'phrase_time_limit',
            'energy_threshold'
        ]
        for config_key in required_config:
            assert config_key in self.config

    def test_listen(self):
        # TODO: Figure out how to mock this
        pass

    def test_recognise_command(self):
        # TODO: Figure out how to mock this
        pass
