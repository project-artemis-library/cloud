class BorgData:
    _shared_state: dict = {}
    data: dict = {}

    def __init__(self):
        self.__dict__ = self._shared_state
