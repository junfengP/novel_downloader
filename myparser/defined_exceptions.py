
class MyBaseException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = str(message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class FetchFailedException(MyBaseException):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()


class EmptyContentException(MyBaseException):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()