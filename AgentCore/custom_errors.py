class InvalidArgumentType(Exception):
    def __init__(self, arg, arg_types):
        self.arg = arg
        self.arg_types = arg_types
        super().__init__(self.arg)

    def __str__(self):
        return f"{self.arg}, does not match the type {self.arg_types}"