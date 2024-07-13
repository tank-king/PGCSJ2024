class State:
    def __init__(self):
        pass


class StateSequence:
    def __init__(self, name, condition_function):
        self.name = name
        self.cond_func = condition_function
