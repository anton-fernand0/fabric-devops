from config import BaseConfig


class App:
    config = None

    @classmethod
    def setup(cls, config: type[BaseConfig]):
        cls.config = config
        return cls
