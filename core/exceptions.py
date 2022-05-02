

class ServiceError(Exception):
    """The service was not able to provide the feed due to an internal error"""


class InputError(Exception):
    """The input provided to the application is invalid"""
