from automatic.models import Configuration


class Config():
    configurations = {}

    def __init__(self):
        if len(Config.configurations) == 0:
            Config.load_configurations()

    @staticmethod
    def load_configurations():
        Config.configurations = {}
        config_types = Configuration.objects.values('type').distinct()
        if len(config_types) > 0:
            for config_type in config_types:
                type = config_type['type']
                confs = {}
                configs = Configuration.objects.filter(type=type, active='Y')
                for config in configs:
                    conf = {}
                    conf['value'] = config.value
                    conf['configuration'] = config.configuration
                    conf['param1'] = config.param1
                    conf['param2'] = config.param2
                    confs[config.name] = conf
                Config.configurations[type] = confs

    @staticmethod
    def load_config_type(type):
        if (type is not None ) and (len(type) > 0):
            confs = {}
            configs = Configuration.objects.filter(type=type, active='Y')
            for config in configs:
                conf = {}
                conf['id'] = config.id
                conf['value'] = config.value
                conf['configuration'] = config.configuration
                conf['param1'] = config.param1
                conf['param2'] = config.param2
                confs[config.name] = conf
            Config.configurations[type] = confs

    @staticmethod
    def get_config(type=None, name=None):
        if type is None or name is None:
            return None
        Config.load_config_type(type)
        if type in Config.configurations:
            config = Config.configurations[type]
            if name in config:
                return config[name]
        return None

    def display_configurations(self):
        print(Config.configurations)

    def has_key(self, key):
        if len(Config.configurations) == 0:
            Config.load_configurations()
        if key in Config.configurations:
            return True
        else:
            return False

    def __getitem__(self, type):
        if len(Config.configurations) == 0:
            Config.load_configurations()
        try:
            if type in Config.configurations:
                return Config.configurations[type]
        except:
            return False
