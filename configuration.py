import json
from astropy.time import Time

class Configuration:

    def __init__(self, config_file):

        if config_file is not None:
            self.load_configuration(config_file)

        self.obs_mode = self.config['obs_mode']
        self.survey_start_time = Time(self.config['default_start_time'])
        self.survey_end_time =  Time(self.config['default_end_time'])
        self.default_scheduling_block_length = int(self.config['default_scheduling_block_length'])
        self.default_timeslot_length = int(self.config['default_timeslot_length'])
        self.default_input_resource = self.config['default_input_resource']
        self.default_input_surveyplan = self.config['default_input_surveyplan']


    def load_configuration(self, config_file):
        with open(config_file, 'r',encoding='utf-8') as f:
            config = json.load(f)
        self.config = config