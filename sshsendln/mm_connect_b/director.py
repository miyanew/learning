from .abstract_session_builder import SessionBuilder


class Director:
    def __init__(self, builder: SessionBuilder):
        self.builder = builder

    def construct(self) -> None:
        self.builder.get_config()
        self.builder.create_bastions()
        self.builder.create_target()
        self.builder.establish_connection()
