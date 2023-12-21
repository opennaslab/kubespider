class UnSupportedMethod(Exception):
    def __init__(self, instance, func_name):
        self.instance = instance
        self.class_name = instance.__class__.__name__
        self.func_name = func_name

    def __repr__(self):
        return f"{self.instance} Is Unsupported To Call {self.class_name}.{self.func_name}"


class StateMachineException(Exception):
    def __init__(self, state, msg):
        self.message = ""

    def __str__(self):
        return self.message
